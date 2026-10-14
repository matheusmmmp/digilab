"""O Paladar, etapa 3 (o cerebro A; docs/futuro/paladar.md, secoes 3.4 a 3.6; PL-1, PL-5, PL-6 e PL-8 pela recomendacao): o canal `gosto`
no sinal e nos canais, as classes `comida:<tipo>` do alvo de comer, os receptores do paladar no modelo do desfecho e o termo do gosto no
planejador.

- G2: a chave desligada e a vida de hoje (o gabarito da etapa 0 em tests/test_paladar_corpo.py, com o cerebro desta etapa);
- a config: os registros, as qualidades iguais as do corpo, as falhas altas, a contagem dos pesos (+3 classes x 3 regras);
- a conta exata do canal gosto (G-FOME: nao le a fome), do credito de uma decisao (o escalar e os canais, com a rota) e de um passo nas
  classes por tipo;
- G-RECEPTOR-PALADAR: o cerebro nao importa o corpo nem o genoma; mudar o perfil de um tipo que o pet nao comeu nao muda o cerebro;
- G-SEM-CREDITO: a fruta na mao nao mexe nos pesos;
- o planejador: o termo do gosto no valor de cada tipo, exato;
- G1 e o motivo.
O lado do mundo e o de verdade (o #309 do A), montado pela `fabrica` de tests/test_paladar_corpo.py.
"""
from __future__ import annotations

import ast
import copy
import sys
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_dois_pets as gdp  # noqa: E402
import test_paladar_corpo as tpc  # noqa: E402

from digilab.config import (CONFIG_CONSEQUENCIA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, CONFIG_PQP_MUNDO_LIGADA,  # noqa: E402
                            ConfigLobos, ConfigPaladar)
from digilab.corpo import QUALIDADES, div_arred  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario, LogDeEventos  # noqa: E402
from digilab.genoma_paladar import genoma_paladar  # noqa: E402
from digilab.motivo import FATORES_VIDA, PoliticaComMotivo  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.mundo import DonoComLugar, reproduzir_mundo, simular_vida_mundo  # noqa: E402
from digilab.policies import lobos  # noqa: E402
from digilab.policies.lobos import (CLASSES_COMER_PALADAR, PARAMETROS_CONSEQUENCIA_N3, QUALIDADES_GOSTO, PoliticaLobos,  # noqa: E402
                                    atualizar_fruta, gosto_previsto, sinal_gosto, valor_previsto, validar_parametros_consequencia,
                                    validar_parametros_lobos)

S = 1024
CM = CONFIG_MUNDO_LIGADA
CC = tpc.QUIMICA_P                                         # o corpo da quimica com o paladar
H = genoma_paladar(101, CC).h
CL = replace(bv.cfg_lobos_do_ponto("T3"), alvo_aprendido=True, presenca_fruta_mundo=True, paladar=True)
CQ = replace(CONFIG_CONSEQUENCIA, canais_ligados=True)


class CerebroEspiao(PoliticaLobos):
    """O cerebro A que confere, em cada credito pelo mundo, a conta exata do gosto, do escalar e do passo nas classes por tipo."""

    conferidos = 0

    def consequencia_mundo(self, acao, ocorrido, obs_depois):
        p = self._corpo_pendente
        antes_alvo = copy.deepcopy(self._pesos_alvo_mundo)
        antes_canais = copy.deepcopy(self._canais)
        super().consequencia_mundo(acao, ocorrido, obs_depois)
        comeu = ocorrido["comeu"]
        if p is None or comeu is None or comeu["situacao"] != "madura":
            return
        cc, S_ = p["cc"], self._escala
        esperado = div_arred(cc.ganho_gosto * sum(div_arred(self._paladar[q] * getattr(obs_depois.corpo, f"paladar_{q}"), S_)
                                                   for q in QUALIDADES), S_)
        sinal = self.motivos[-1]["sinal_corpo"]
        assert sinal["gosto"] == esperado
        f_total = sinal["f"] + esperado
        sub = p["registro"].get("alvo_mundo")
        if sub is not None:
            # o passo nas classes: a regra da sub-decisao da fruta com o sinal inteiro da decisao (os drives e o gosto)
            tabela = dict(antes_alvo[sub["chave"]])
            atualizar_fruta(tabela, self._prior_alvo_mundo[sub["chave"]], sub, f_total, self.cl.passo, self.cl.teto, S_)
            assert self._pesos_alvo_mundo[sub["chave"]] == tabela
        if cc.canais_ligados:
            antes = 0 if antes_canais is None else antes_canais["por_canal"]["gosto"]
            assert self._canais["por_canal"]["gosto"] - antes == esperado
        type(self).conferidos += 1


def cerebro(cl=CL, h=H, classe=PoliticaLobos, **kw) -> PoliticaLobos:
    return classe(CONFIG_PADRAO, cl, cfg_mundo=CM, cfg_corpo=CC, h_paladar=h, **kw)


def vida(semente=101, dias=3, cq=CQ, classe=PoliticaLobos, cl=CL, fabrica=None, embrulho=None, **kw):
    c = cerebro(cl, classe=classe, **kw)
    p = bv.PoliticaDoBraco(c, bv.braco_de("P1"), cq)
    if embrulho is not None:
        p = embrulho(p)
    dono = DonoComLugar(criar_dono("atencioso"), "comedouro", semente, "atencioso", CM)
    v = simular_vida_mundo("atencioso", dono, p, semente, dias, 16 * dias, fabrica or tpc.fabrica(CC), rotulo_dono="atencioso")
    return v, c


# ================================================================== a config
def test_os_registros_e_as_qualidades():
    validar_parametros_lobos()
    validar_parametros_consequencia()
    assert "ganho_gosto" in PARAMETROS_CONSEQUENCIA_N3 and CONFIG_CONSEQUENCIA.ganho_gosto == S
    assert QUALIDADES_GOSTO == QUALIDADES                                         # o cerebro nao importa o corpo; confere aqui
    assert not ConfigLobos().paladar


def test_as_falhas_altas():
    with pytest.raises(ValueError, match="ConfigLobos.paladar exige"):
        PoliticaLobos(CONFIG_PADRAO, CL, cfg_mundo=CM, cfg_corpo=replace(CC, paladar=False), h_paladar=H)
    with pytest.raises(ValueError, match="ConfigLobos.paladar exige"):
        cerebro(replace(CL, alvo_aprendido=False))
    with pytest.raises(ValueError, match="h_q"):
        cerebro(h=None)
    with pytest.raises(ValueError, match="fora de inteiros"):
        cerebro(h={**H, "doce": 2 * S})
    with pytest.raises(ValueError, match="sem ConfigLobos.paladar"):
        cerebro(replace(CL, paladar=False))
    with pytest.raises(TypeError, match="bool"):
        cerebro(replace(CL, paladar=1))
    with pytest.raises(ValueError, match="ganho_gosto"):
        replace(CONFIG_CONSEQUENCIA, ganho_gosto=-1)


def test_a_contagem_dos_pesos():
    """+3 classes (comida por tipo no lugar de comida) x 3 regras em que o comer tem alvo; no P1 do J5 (com as arvores), 822 -> 831"""
    sem = PoliticaLobos(CONFIG_PADRAO, replace(CL, paladar=False), cfg_mundo=CM, cfg_corpo=CC)
    assert cerebro().n_pesos() == sem.n_pesos() + 9
    j5 = replace(CL, alvo_por_arvore=True)
    assert cerebro(j5).n_pesos() == 831
    assert PoliticaLobos(CONFIG_PADRAO, replace(j5, paladar=False), cfg_mundo=CM, cfg_corpo=CC).n_pesos() == 822
    c = cerebro()
    for r in ("pedido_necessidade", "fome_moderada", "fruta_no_cenario"):
        assert tuple(c._prior_alvo_mundo[f"{r}:comer"]) == CLASSES_COMER_PALADAR
        assert set(c._prior_alvo_mundo[f"{r}:comer"].values()) == {CL.w0_alvo}      # o querer sem atracao inata (PL-5)


# ================================================================== a conta exata e G-FOME
def _pc(paladar: dict, **drives) -> PercepcaoCorpo:
    base = {"fome": 600, "higiene": 900, "energia": 800, "humor": 700, "saude": 1000}
    return PercepcaoCorpo(**{**base, **drives}, **{f"paladar_{q}": paladar[q] for q in QUALIDADES})


def test_a_conta_exata_do_canal_gosto_e_g_fome():
    h = {"doce": 1000, "azedo": -300, "amargo": 7, "salgado": 256}
    r = {"doce": 768, "azedo": 256, "amargo": 0, "salgado": 13}
    esperado = div_arred(2048 * (div_arred(1000 * 768, S) + div_arred(-300 * 256, S) + 0 + div_arred(256 * 13, S)), S)
    assert sinal_gosto(_pc(r), h, 2048, S) == esperado == div_arred(2048 * (750 - 75 + 3), S)
    # G-FOME: a fome (e todo drive) nao muda o gosto
    assert {sinal_gosto(_pc(r, fome=f, energia=e), h, 2048, S) for f in (0, 300, 1024) for e in (0, 1024)} == {esperado}
    assert sinal_gosto(_pc(dict.fromkeys(QUALIDADES, 0)), h, 2048, S) == 0
    with pytest.raises(ValueError):
        sinal_gosto(_pc(r), h, -1, S)


def test_o_credito_de_cada_comida_madura_conta_exata():
    """numa vida (P1, canais ligados), cada credito com comida madura: o gosto e o da conta sobre os receptores de depois, o passo nas
    classes e a regra da sub-decisao com o sinal inteiro (drives mais gosto), e o canal gosto acumula exatamente o gosto"""
    CerebroEspiao.conferidos = 0
    v, c = vida(classe=CerebroEspiao)
    assert CerebroEspiao.conferidos >= 5
    assert c._n_recompensas["gosto"] == CerebroEspiao.conferidos
    # a rota: o gosto nunca vai a tabela do corpo (so os canais dos drives); a soma dos canais e o escalar (K-6, conferido no credito)
    assert lobos.ROTA_CANAL_GOSTO == {"gosto": "fruta"}


def test_o_escalar_sem_canais_tambem_leva_o_gosto():
    CerebroEspiao.conferidos = 0
    vida(classe=CerebroEspiao, cq=CONFIG_CONSEQUENCIA)
    assert CerebroEspiao.conferidos >= 5


def test_as_classes_por_tipo_na_vida():
    v, c = vida()
    classes = [m["alvo_aprendido"]["classes"] for m in c.motivos if "alvo_aprendido" in m and m["alvo_aprendido"]["classes"]]
    comer = [cl for cl in classes if any(x.startswith("comida") for x in cl)]
    assert comer and not any("comida" in cl for cl in comer)                       # nunca a classe sem tipo
    vistas = {x for cl in comer for x in cl if x.startswith("comida:")}
    assert "comida:racao" in vistas
    movidas = {cl for k, t in c._pesos_alvo_mundo.items() if k.endswith(":comer") for cl, w in t.items()
               if w != c._prior_alvo_mundo[k][cl]}
    assert any(x.startswith("comida:") for x in movidas)                          # as classes por tipo aprendem


# ================================================================== G-RECEPTOR-PALADAR e G-SEM-CREDITO
def test_g_receptor_paladar_o_cerebro_nao_importa_o_corpo():
    arvore = ast.parse((RAIZ / "digilab" / "policies" / "lobos.py").read_text(encoding="utf-8"))
    modulos = {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom) and n.module}
    assert not {m for m in modulos if m.endswith("corpo") or "genoma_paladar" in m or m.endswith("motor_corpo")}


def test_g_receptor_paladar_o_perfil_de_um_tipo_nao_comido_nao_muda_o_cerebro():
    v, c = vida()
    comidos = {x["tipo"] for x in v.motor.consumos_mundo if x["situacao"] == "madura"}
    nao_comido = next(t for t in ("c", "b", "a") if t not in comidos)
    outro = {**tpc.PERFIS, nao_comido: dict.fromkeys(QUALIDADES, 7)}

    v2, c2 = vida(fabrica=tpc.fabrica(CC, cpal=ConfigPaladar(ligada=True, perfis=outro)))
    assert c2.estado_interno() == c.estado_interno()
    assert gdp.impressao(v2.motor) == gdp.impressao(v.motor)
    assert v2.motor.cpal.perfis[nao_comido] != v.motor.cpal.perfis[nao_comido]       # o mundo mudou de verdade


def test_g_sem_credito_a_fruta_na_mao():
    c = cerebro(replace(CL, alvo_por_arvore=True, g_plano=S), cfg_consequencia=CQ)
    p = bv.PoliticaDoBraco(c, bv.braco_de("P1"), CQ)
    m = tpc.fabrica(CC)(p, CONFIG_PADRAO, 101, cfg_pqp=CONFIG_PQP_MUNDO_LIGADA)
    m.avancar(600)
    antes = copy.deepcopy(c.estado_interno())
    sabor_antes = dict(m.corpo.q)
    m.observar(AcaoUsuario.DAR_FRUTA_A)
    assert m.corpo.q["saciedade_doce"] > sabor_antes["saciedade_doce"]             # o gosto chegou ao corpo
    depois = c.estado_interno()
    tirar = lambda d: {k: ({kk: vv for kk, vv in v.items() if kk != "modelo_mundo"} if k == "plano" else v)  # noqa: E731
                       for k, v in d.items()}
    assert tirar(depois) == tirar(antes)                                           # nenhum peso, motivo ou recompensa mudou


# ================================================================== o planejador
def test_o_planejador_soma_o_termo_do_gosto_exato():
    v, c = vida(cl=replace(CL, alvo_por_arvore=True, g_plano=S), cfg_consequencia=CQ)
    mm = c.modelo_mundo
    assert {f"paladar_{q}" for q in QUALIDADES} <= set(mm.receptores)            # os receptores do paladar no desfecho
    pc = _pc({"doce": 5, "azedo": 0, "amargo": 3, "salgado": 900})
    valores = c._valores_do_plano(pc)
    for t, valor in valores.items():
        d = mm.desfecho_de(t)
        base = valor_previsto(pc, d, c._drives_plano, CQ.ganho, S, dict(CQ.pesos_drives_corpo))
        assert valor == base + (0 if t == "podre" else gosto_previsto(pc, d, H, CQ.ganho_gosto, S))
    comidos = {x["tipo"] for x in v.motor.consumos_mundo if x["situacao"] == "madura"}
    assert comidos and all(any(mm.desfecho_de(t)[f"paladar_{q}"] for q in QUALIDADES) for t in comidos)   # o desfecho aprendeu o gosto


# ================================================================== G1 e o motivo
def test_g1_o_replay_refaz_o_cerebro_com_o_paladar():
    v, c = vida(202)
    fp = lambda cfg=None: bv.PoliticaDoBraco(cerebro(), bv.braco_de("P1"), CQ)  # noqa: E731
    r = reproduzir_mundo(LogDeEventos.de_jsonl(v.motor.log.para_jsonl()), fp, CONFIG_PADRAO, 202, fabrica_motor=tpc.fabrica(CC))
    assert r.politica.cerebro.estado_interno() == c.estado_interno()
    assert gdp.impressao(r) == gdp.impressao(v.motor)


def test_o_motivo_com_o_paladar():
    """embrulhado no PoliticaComMotivo, a vida e a mesma e todo fator e um dos de sempre (nenhum texto novo diz que o pet acha gostoso)"""
    v, c = vida(embrulho=PoliticaComMotivo)
    w, d = vida()
    m = v.motor.politica
    assert len(m.motivos) == len(c.motivos) > 0
    assert all(set(mot.fatores) <= set(FATORES_VIDA) for mot in m.motivos)
    assert c.estado_interno() == d.estado_interno()
