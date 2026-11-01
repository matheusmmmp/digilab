"""C4, M0 e M1 (docs/ESPEC_MEMORIA_AUTOBIOGRAFICA_DIGIBRAIN_MODULAR.md, secoes 3, 8 e 9; MA-1 a MA-8 DECIDIDAS em 2026-11-01): a subchave
`memoria_autobio` do DigiBrain modular, o episodio completo e a codificacao, antes de qualquer vida de pesquisa. So as sementes 101 a 505
e sequencias sinteticas.

  - G2: com ela desligada, as vidas de hoje saem byte a byte (tests/test_gabarito_memoria_autobio.py, o gabarito do M3* gravado antes,
    mais os da C3, da C2, do conserto e do modular); aqui, o que a desligada nao cria (campo, estado);
  - G2-SEPARADO: ligada, ela muda so a vida do braco que a liga, e nas M0 e M1 nem a escolha (o log sai o mesmo); nada fora do pacote
    `digibrain` le a chave;
  - G1: o replay de cada vida com ela ligada, nas cinco sementes;
  - T-ME-0: o episodio sai igual no replay; o M-MEM so recebe o que o cerebro recebeu (pela AST); nenhum campo de fora da Observacao;
  - T-ME-1: um evento forte vira episodio e um neutro nao; o afeto pela subida de dor, susto ou estresse >= `theta_sig`, nao pelo nivel
    (o Matheus, 2026-11-01, no #530); o mesmo log codifica os mesmos episodios; a visita vazia com sigma = min(0, r da ida);
  - a rng; G-MECANISMO, G-INT, G-SEM-DIRECAO e G-RECEPTOR com ela ligada."""
from __future__ import annotations

import ast
import copy
import inspect
import json
import sys
from dataclasses import fields, replace
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
import test_digibrain_mecanismo as tm  # noqa: E402
from test_digibrain_mecanismo import RngContada  # noqa: E402

from digilab.config import (CONFIG_DIGIBRAIN, CONFIG_DIGIBRAIN_INATOS, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            PARAMETROS_DIGIBRAIN_INATOS, RECEPTORES_DIGIBRAIN, TICKS_POR_DIA, ConfigDigibrain, ConfigDigibrainInatos)
from digilab.digibrain import mem as M  # noqa: E402
from digilab.digibrain.arb import Arbitragem  # noqa: E402
from digilab.digibrain.ganchos import CAMPOS_POR_MODULO  # noqa: E402

P = CONFIG_DIGIBRAIN_INATOS
S = P.escala
SEMENTES = (101, 202, 303, 404, 505)
BASE = replace(CONFIG_DIGIBRAIN_LIGADA, cheiro_inato=True, intencao_cheiro=True)
LIGADA = replace(BASE, memoria_autobio=True)
# os campos do episodio (a tabela 3.1 da espec, sem os da M3 que a M0 so cria) e os que o M-MEM poe ao guardar
CAMPOS_EPISODIO = {"decisao", "tick", "ponto", "regiao", "vista", "cheiro", "noite", "acao", "objeto", "dono", "outro", "corpo_antes",
                   "corpo_depois", "delta", "V_antes", "V_depois", "E_antes", "E_depois", "r", "r_n", "sigma", "classe", "origem",
                   "categoria", "fome_antes", "hora", "rep", "rec", "memoria"}
CAMPOS_GUARDADOS = CAMPOS_EPISODIO | {"id", "lugar"}


# ------------------------------------------------------------------ as pecas sinteticas
def sens(objetos=(), ha_cheiro=False, noite=0, fome=300) -> dict:
    return {"objetos": list(objetos), "ha_cheiro": ha_cheiro, "contexto": {"noite": noite}, "falta": {"fome": fome}, "minuto": 600}


def leituras(**kw) -> list:
    return [kw.get(r, 0) for r in RECEPTORES_DIGIBRAIN]


PM1 = SimpleNamespace(x=40, y=72, regiao=1)
COMIDA = {"id": 7, "tipo": "a", "classe": "a", "dx": 1, "dy": 0, "d": 30, "prox": 900, "nov": 0}
BOLA = {"id": 3, "tipo": "bola", "classe": "bola", "dx": 0, "dy": 2, "d": 50, "prox": 800, "nov": 0}


def unidade(chave: tuple, objeto=None) -> dict:
    return {"chave": chave, "acao": chave[0], "tipo": chave[1], "objeto": objeto, "d": None}


def episodio(r_n=0, depois=None, unid=None, comeu=None, chegou=False, r_ida=None, objetos=(), gestos=(), antes=None):
    return M.episodio_autobio(sens(objetos), PM1, RECEPTORES_DIGIBRAIN, antes or leituras(), depois or leituras(), {"V": 5, "E": 9},
                              {"r": 2 * r_n, "r_n": r_n, "V": 6, "E": 10}, list(gestos), unid or unidade(("ocioso", None, None)),
                              {"comeu": comeu, "chegou": chegou, "r_ida": r_ida}, 4, 75, P)


def _sem_float(x) -> bool:
    if isinstance(x, float):
        return False
    if isinstance(x, dict):
        return all(isinstance(k, str) and _sem_float(v) for k, v in x.items())
    if isinstance(x, (list, tuple)):
        return all(_sem_float(v) for v in x)
    return x is None or isinstance(x, (int, str))


# ------------------------------------------------------------------ a subchave e os campos
def test_a_subchave_nasce_desligada_e_so_aceita_bool():
    assert CONFIG_DIGIBRAIN.memoria_autobio is False and CONFIG_DIGIBRAIN_LIGADA.memoria_autobio is False
    with pytest.raises(TypeError, match="memoria_autobio"):
        ConfigDigibrain(memoria_autobio=1)


@pytest.mark.parametrize("extra", [{"m_mem": False}, {"credito_corrida": True}, {"intencao_suspensa": True},
                                   {"redecidir_evento": True}, {"cheiro_inato": False}, {"intencao_cheiro": False}])
def test_a_subchave_recusa_as_combinacoes_da_ma_7(extra):
    with pytest.raises(ValueError, match="memoria_autobio"):
        replace(LIGADA, **extra)


def test_os_campos_da_m1_sao_os_da_secao_8_decididos_no_modulo_mem():
    assert (P.theta_sig, P.n_rec) == (S // 8, 16) == (128, P.n_ep)
    assert "theta_afeto" not in {f.name for f in fields(ConfigDigibrainInatos)}       # removido em 2026-11-01 (comentario do PR #532)
    assert "theta_afeto" not in CAMPOS_POR_MODULO["mem"]
    for c in ("theta_sig", "n_rec"):
        assert c in CAMPOS_POR_MODULO["mem"] and PARAMETROS_DIGIBRAIN_INATOS[c][0] == "DECIDIDO"
        assert "SEM FONTE" in PARAMETROS_DIGIBRAIN_INATOS[c][1]
    assert {f.name for f in fields(ConfigDigibrainInatos)} == {c for cs in CAMPOS_POR_MODULO.values() for c in cs}
    for kw in ({"n_rec": 0}, {"theta_sig": 0}, {"theta_sig": S + 1}):
        with pytest.raises(ValueError, match="theta_sig"):
            ConfigDigibrainInatos(**kw)


def test_desligada_o_estado_e_o_motivo_nao_tem_campo_novo():
    mem = M.Memoria(CONFIG_MUNDO_LIGADA)
    assert "autobio" not in mem.estado_interno() and not hasattr(mem, "recente")
    with pytest.raises(RuntimeError, match="memoria_autobio"):
        mem.relogio(0)
    with pytest.raises(RuntimeError, match="memoria_autobio"):
        mem.codificar_autobio(episodio(r_n=500))
    c = orq.cerebro_de(_viver(101, ligada=False)[1])
    assert "autobio" not in c.m.mem.estado_interno()
    assert not any("autobio" in m["consequencia"] for m in c.motivos if m["consequencia"])


# ------------------------------------------------------------------ T-ME-0: o formato
def test_t_me_0_o_episodio_tem_os_campos_da_tabela_3_1_sem_float():
    ep = episodio(r_n=300, unid=unidade(("comer", "comida", 7), COMIDA), objetos=[COMIDA, BOLA], gestos=[["carinho", 30], ["tapa", 40]])
    assert set(ep) == CAMPOS_EPISODIO and _sem_float(ep)
    assert ep["vista"] == ["a", "bola"] and ep["objeto"] == {"id": 7, "classe": "a"} and ep["dono"] == ["carinho", "tapa"]
    assert ep["outro"] is None and ep["acao"] == ["comer", "comida", 7] and ep["tick"] == 75 and ep["decisao"] == 4
    assert set(ep["corpo_antes"]) == set(ep["corpo_depois"]) == set(ep["delta"]) == set(RECEPTORES_DIGIBRAIN)
    assert (ep["V_antes"], ep["V_depois"], ep["E_antes"], ep["E_depois"]) == (5, 6, 9, 10)
    assert (ep["rep"], ep["rec"], ep["memoria"]) == (0, 0, "recente")


def test_t_me_0_o_m_mem_so_recebe_o_que_o_cerebro_recebeu():
    """pela AST: o mem.py importa so a config, a geometria inteira, a conta inteira do A e o _comum (nenhum objeto do motor), e o
    episodio so tem os parametros da Observacao, dos receptores, do afeto, dos gestos, da unidade e do desfecho que o M-ADAPT ja le"""
    arvore = ast.parse(inspect.getsource(M))
    origens = {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)}
    assert origens == {"__future__", "config", "modelo_mundo", "policies.lobos", "_comum"}
    assert not any(isinstance(n, ast.Import) for n in ast.walk(arvore))
    assert list(inspect.signature(M.episodio_autobio).parameters) == [
        "sens", "pm1", "recs", "l0", "l1", "afeto_antes", "cons", "gestos", "unidade", "desfecho", "k", "tick", "p"]
    fonte = inspect.getsource(M.episodio_autobio)
    assert "pc" not in {n.attr for n in ast.walk(ast.parse(fonte.strip())) if isinstance(n, ast.Attribute)}
    assert "direcao" not in fonte and "random" not in inspect.getsource(M)


def test_t_me_0_nenhum_campo_do_estado_privado_nas_vidas():
    for c in (orq.cerebro_de(_viver(s)[1]) for s in (101, 303)):
        recente = c.m.mem.estado_interno()["autobio"]["recente"]
        assert recente and all(set(e) == CAMPOS_GUARDADOS and _sem_float(e) for e in recente)
        assert all(set(e["corpo_antes"]) == set(c.m.sens.receptores) for e in recente)
        json.dumps(recente)


# ------------------------------------------------------------------ T-ME-1: a codificacao
def test_t_me_1_um_evento_forte_vira_episodio_e_um_neutro_nao():
    assert episodio(r_n=P.theta_sig - 1) is None and episodio(r_n=-(P.theta_sig - 1)) is None
    assert episodio(r_n=0, depois=leituras(estresse=P.theta_sig - 1, dor=10, fome=S)) is None     # a fome nao e afetiva
    forte = episodio(r_n=P.theta_sig)
    assert forte["origem"] == "evento" and forte["sigma"] == P.theta_sig and forte["categoria"] == ["ocioso", "sem_alvo", 1]
    ruim = episodio(r_n=-P.theta_sig, unid=unidade(("brincar", "bola", 3), BOLA), objetos=[BOLA])
    assert ruim["classe"] == "bola" and ruim["categoria"] == ["brincar", "bola", -1]
    for r in ("dor", "susto", "estresse"):
        susto = episodio(r_n=0, depois=leituras(**{r: P.theta_sig}))
        assert susto["origem"] == "evento" and susto["sigma"] == 0 and susto["categoria"] == ["ocioso", "sem_alvo", 0]


@pytest.mark.parametrize("r", M.AFETIVOS)
def test_t_me_1_o_afeto_e_a_subida_na_decisao_e_nao_o_nivel(r):
    """a espec 3.3 (o Matheus, 2026-11-01, no #530): a maior subida de dor, susto ou estresse (depois - antes, so os aumentos) >=
    theta_sig; o theta_afeto saiu"""
    base = 300
    assert episodio(antes=leituras(**{r: base}), depois=leituras(**{r: base + P.theta_sig - 1})) is None   # abaixo do limiar
    no_limiar = episodio(antes=leituras(**{r: base}), depois=leituras(**{r: base + P.theta_sig}))
    assert no_limiar["origem"] == "evento" and no_limiar["delta"][r] == P.theta_sig
    assert episodio(antes=leituras(**{r: S}), depois=leituras(**{r: S})) is None                        # alto e parado
    assert episodio(antes=leituras(**{r: S}), depois=leituras(**{r: S - P.theta_sig})) is None          # a queda nao conta
    # uma queda noutro afetivo nao apaga a subida deste; o nivel alto sem subir nao conta
    outro = next(o for o in M.AFETIVOS if o != r)
    assert episodio(antes=leituras(**{r: 0, outro: S}), depois=leituras(**{r: P.theta_sig, outro: 0}))["origem"] == "evento"
    assert episodio(antes=leituras(**{r: S // 2}), depois=leituras(**{r: S // 2 + 1})) is None
    assert episodio(antes=leituras(fome=0), depois=leituras(fome=S)) is None                            # a fome nao e afetiva


def test_t_me_1_o_consumo_vira_episodio_sempre_com_a_classe_comida():
    ep = episodio(r_n=5, unid=unidade(("comer", "comida", 7), COMIDA), comeu="a", objetos=[COMIDA])
    assert ep["origem"] == "consumo" and ep["classe"] == "a" and ep["sigma"] == ep["r_n"] == 5 and ep["ponto"] == (40, 72)
    podre = episodio(r_n=-400, unid=unidade(("explorar", "cheiro", None)), comeu="podre")
    assert podre["categoria"] == ["explorar", "podre", -1] and podre["objeto"] is None


def test_t_me_1_a_visita_vazia_tem_sigma_min_0_r_da_ida():
    ponto = unidade(("explorar", "ponto", (100, 200)))
    cara = episodio(r_n=-30, unid=ponto, chegou=True, r_ida=-300)
    assert cara["origem"] == "visita" and cara["classe"] == "nao_havia" and cara["sigma"] == -300 and cara["ponto"] == (100, 200)
    assert cara["categoria"] == ["explorar", "nao_havia", -1] and cara["r"] == cara["r_n"] == 0          # o r de hoje, forcado a 0
    boa = episodio(r_n=200, unid=ponto, chegou=True, r_ida=150)                     # nada se achou: nunca positivo (MA-1)
    assert boa["sigma"] == 0 and boa["categoria"] == ["explorar", "nao_havia", 0]
    with pytest.raises(ValueError, match="r da ida"):
        episodio(unid=ponto, chegou=True, r_ida=None)
    assert episodio(r_n=0, unid=ponto, chegou=False) is None                        # a ida sem chegar e um evento como os outros


def test_t_me_1_a_recente_cheia_descarta_o_de_menor_sigma_e_registra():
    mem = M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True)
    sigmas = [300, -200, 500, 200] + [400] * (P.n_rec - 4)
    for k, s in enumerate(sigmas):
        mem.codificar_autobio({**episodio(r_n=s), "decisao": k, "ponto": (k * 10_000, 0)})   # um lugar por episodio: rep = 0
    mem.codificar_autobio({**episodio(r_n=900), "decisao": P.n_rec, "ponto": (10_000_000, 0)})
    assert mem.saidas_autobio == [{"id": 1, "sigma": -200}]                         # |-200| = |200|: sai o mais antigo
    mem.codificar_autobio({**episodio(r_n=900), "decisao": P.n_rec + 1, "ponto": (20_000_000, 0)})
    assert mem.saidas_autobio[-1] == {"id": 3, "sigma": 200} and len(mem.recente) == P.n_rec
    with pytest.raises(ValueError, match="visita"):
        mem.codificar_autobio({**episodio(r_n=500), "origem": "visita", "classe": "nao_havia", "sigma": 1})


def test_o_relogio_avanca_o_dia_quando_a_hora_volta():
    mem = M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True)
    assert [mem.relogio(m) for m in (0, 15, TICKS_POR_DIA - 15, 0, 30)] == [0, 15, TICKS_POR_DIA - 15, TICKS_POR_DIA,
                                                                              TICKS_POR_DIA + 30]
    with pytest.raises(ValueError, match="hora"):
        mem.relogio(TICKS_POR_DIA)


# ------------------------------------------------------------------ T-ME-2: a lembranca e o lugar pela soma
def pista(pos=(40, 72), objetos=(), ha_cheiro=False, noite=0, **corpo) -> dict:
    return {**sens(objetos, ha_cheiro, noite), "pos": pos, "leitura": dict(zip(RECEPTORES_DIGIBRAIN, leituras(**corpo)))}


def guardar(mem, r_n=300, ponto=(40, 72), decisao=0, **kw):
    """codifica um episodio sintetico: kw vai a `episodio`; `ponto` e `decisao` sao postos depois"""
    return mem.codificar_autobio({**episodio(r_n=r_n, **kw), "ponto": ponto, "decisao": decisao})


def nova() -> M.Memoria:
    return M.Memoria(CONFIG_MUNDO_LIGADA, autobio=True)


def mover(mem, ep, para: str) -> None:
    """poe o episodio da recente na duradoura ou na central (so o teste faz isto; o `consolidar` e quem faz na vida)"""
    mem.recente.remove(ep)
    ep["memoria"] = para
    getattr(mem, para).append(ep)


def test_t_me_2_um_contexto_conhecido_recupera_o_episodio_certo():
    mem = nova()
    longe = guardar(mem, 300, ponto=(900, 900), objetos=[BOLA], decisao=1, antes=leituras(fome=900))
    certo = guardar(mem, 300, ponto=(40, 72), objetos=[COMIDA], decisao=2)
    rec = mem.lembrar(pista(objetos=[COMIDA]))
    assert rec["recuperado"] == certo and rec["sim"] == S and rec["memoria"] == "recente" and rec["sigma"] == 300
    assert mem.recente[1]["rec"] == 1 and mem.recente[0]["rec"] == 0 and mem.lembrancas == 1
    assert mem.lembrar(pista(pos=(900, 900), objetos=[BOLA], fome=900))["recuperado"] == longe


def test_t_me_2_um_contexto_novo_nao_recupera_nada():
    mem = nova()
    guardar(mem, 300, objetos=[COMIDA])
    novo = mem.lembrar(pista(pos=(900, 900), objetos=[BOLA], ha_cheiro=True, noite=S, fome=900, dor=900))
    assert novo["recuperado"] is None and 0 <= novo["sim"] < P.sim_min and mem.recente[0]["rec"] == 0 and mem.lembrancas == 0
    assert nova().lembrar(pista()) == {"recuperado": None, "sim": 0, "memoria": None, "sigma": 0}      # sem episodio


def test_t_me_2_a_semelhanca_e_a_media_ponderada_inteira():
    assert (P.w_lugar, P.w_vista, P.w_corpo, P.sim_min) == (2, 1, 1, 3 * S // 4)
    mem = nova()
    guardar(mem, 300, ponto=(40, 72), objetos=[COMIDA])                        # vista {a}; o corpo todo na faixa 0
    # a pista: no lugar, vista {a, bola} (Jaccard 1/2), o corpo igual em 10 dos 11 (a fome subiu de faixa)
    rec = mem.lembrar(pista(objetos=[COMIDA, BOLA], fome=S // 2))
    s_vista, s_corpo = (1 * S + 1) // 2, (10 * S + 5) // 11
    assert abs(rec["sim"] - (2 * S + s_vista + s_corpo) // 4) <= 1 and rec["sim"] >= P.sim_min
    vazio = nova()
    guardar(vazio, 300, ponto=(40, 72))                                         # as duas vazias: s_vista = S
    assert vazio.lembrar(pista())["sim"] == S


def test_t_me_2_o_empate_desfaz_por_ordem_fixa_sem_rng():
    for primeiro_forte in (True, False):                                        # a ordem de guardar nao decide
        mem = nova()
        forte, fraco = (400, 150) if primeiro_forte else (150, 400)
        a = guardar(mem, forte, decisao=1)
        b = guardar(mem, fraco, decisao=2)
        assert mem.lembrar(pista())["recuperado"] == (a if primeiro_forte else b)       # o maior |sigma|
    mem = nova()
    antigo = guardar(mem, 300, decisao=1)
    recente = guardar(mem, -300, decisao=7)                                     # o mesmo |sigma|: o mais recente
    assert mem.lembrar(pista())["recuperado"] == recente != antigo


def test_t_me_2_as_tres_memorias_entram_na_lembranca():
    mem = nova()
    i = guardar(mem, 300, decisao=0)
    j = guardar(mem, 300, decisao=1)
    k = guardar(mem, 300, decisao=2)
    mover(mem, mem.recente[0], "duradoura")
    mover(mem, mem.recente[0], "central")
    assert mem.lembrar(pista())["recuperado"] == k and mem.lembrar(pista())["memoria"] == "recente"
    mem.recente.clear()
    assert mem.lembrar(pista())["recuperado"] == j and mem.lembrar(pista())["memoria"] == "central"     # a central, a mais recente
    mem.central.clear()
    assert mem.lembrar(pista())["recuperado"] == i and mem.lembrar(pista())["memoria"] == "duradoura"


def test_t_me_2_so_com_a_subchave():
    with pytest.raises(RuntimeError, match="memoria_autobio"):
        M.Memoria(CONFIG_MUNDO_LIGADA).lembrar(pista())


SEM = {"pos": (100, 100), "conjuncoes": {"comida_vista": 0}}
FOME = {"urgencias": {"fome": S}}
COMER = unidade(("comer", "comida", 7), COMIDA)


def ida_vazia(ponto, r_ida):
    return {"unid": unidade(("explorar", "ponto", ponto)), "chegou": True, "r_ida": r_ida, "ponto": ponto}


def test_t_me_2_o_valor_do_lugar_e_a_soma_dos_sigma_nas_tres_memorias():
    mem = nova()
    guardar(mem, 500, ponto=(400, 100), unid=COMER, comeu="a", decisao=0)
    rec = mem.recuperar(SEM, FOME)
    assert rec["recuperado"] == 0 and rec["ponto"] == (400, 100) and rec["valor"] == 500 and rec["M"] == (P.w_mem * 500) // S
    guardar(mem, 0, **ida_vazia((402, 101), -200), decisao=5)
    rec = mem.recuperar(SEM, FOME)
    assert rec["valor"] == 300 and rec["recuperado"] == 1                        # uma ida vazia que custou pouco nao apaga o lugar
    mover(mem, mem.recente[0], "duradoura")                                      # a soma le as tres memorias
    assert mem.recuperar(SEM, FOME)["valor"] == 300
    guardar(mem, 0, **ida_vazia((403, 101), -900), decisao=9)
    assert mem.recuperar(SEM, FOME)["recuperado"] is None                        # a ida que custou mais que a refeicao: lugar negativo
    guardar(mem, 0, **ida_vazia((405, 101), 0), decisao=11)                      # sigma = 0: nao pesa (o braco sem negativos)
    assert mem.valores_soma()[(400 // mem.sub, 100 // mem.sub)][0] == 500 - 200 - 900


def test_t_me_2_so_consumo_de_comida_boa_e_visita_entram_na_soma():
    mem = nova()
    guardar(mem, 500, ponto=(400, 100), unid=COMER, comeu="podre")
    guardar(mem, 900, ponto=(400, 100), decisao=1)                               # um evento
    assert mem.valores_soma() == {} and mem.recuperar(SEM, FOME)["recuperado"] is None
    guardar(mem, 5000, ponto=(400, 100), unid=COMER, comeu="b", decisao=2)
    assert mem.valores_soma()[(400 // mem.sub, 100 // mem.sub)][0] == S             # cortada em [-S, S]
    assert mem.recuperar({**SEM, "conjuncoes": {"comida_vista": 10}}, FOME)["recuperado"] is None     # a pista de hoje segue


def test_t_me_2_comidas_boas_iguais_as_do_msens():
    from digilab.digibrain.sens import COMIDAS_BOAS
    assert tuple(M.COMIDAS_BOAS) == tuple(COMIDAS_BOAS)


# ------------------------------------------------------------------ T-ME-3: a consolidacao
def virar_dia(mem, dias=1):
    for _ in range(dias):
        mem.relogio(600)
        mem.relogio(0)


def test_t_me_3_a_repeticao_soma_no_guardado_com_mesma_categoria_e_lugar():
    mem = nova()
    guardar(mem, 300, decisao=0)
    guardar(mem, 300, decisao=1)
    guardar(mem, 300, decisao=2, ponto=(900, 900))                               # outro lugar
    guardar(mem, -300, decisao=3)                                                # outro sinal: outra categoria
    assert [e["rep"] for e in mem.recente] == [1, 0, 0, 0]


def test_t_me_3_um_episodio_repetido_consolida_e_um_esquecido_some():
    mem = nova()
    repetido = guardar(mem, 150, decisao=0)
    repete = guardar(mem, 150, decisao=1)                                        # repete o primeiro: rep = 1 no primeiro
    esquecido = guardar(mem, 150, decisao=2, ponto=(900, 900))                   # rep 0, rec 0, |sigma| < theta_dur
    forte = guardar(mem, P.theta_dur, decisao=3, ponto=(500, 500))
    lembrado = guardar(mem, 150, decisao=4, ponto=(700, 100), objetos=[BOLA])
    assert mem.lembrar(pista(pos=(700, 100), objetos=[BOLA]))["recuperado"] == lembrado        # rec = 1
    tarde = guardar(mem, 150, decisao=250, ponto=(1000, 1000))                   # dentro da janela: fica
    virar_dia(mem)
    reg = mem.consolidar(P.janela_rec + 5)
    assert mem.consolidar(P.janela_rec + 6) is None                              # uma vez por dia
    assert sorted(reg["subiram"]["duradoura"]) == sorted([repetido, forte, lembrado])
    assert sorted(reg["esquecidos"]) == sorted([repete, esquecido])              # o que repete, sem repeticao propria, tambem some
    assert {e["id"] for e in mem.duradoura} == {repetido, forte, lembrado} and all(e["memoria"] == "duradoura" for e in mem.duradoura)
    assert [e["id"] for e in mem.recente] == [tarde] and esquecido not in {e["id"] for e in mem._guardados()}
    assert mem.consolidacoes == [reg] and mem.estado_interno()["autobio"]["consolidacoes"] == [reg]


def test_t_me_3_a_janela_e_estrita_e_o_dia_e_o_do_relogio():
    mem = nova()
    guardar(mem, 150, decisao=0)
    assert mem.consolidar(500) is None                                           # sem virada do dia, nada
    virar_dia(mem)
    assert mem.consolidar(P.janela_rec)["esquecidos"] == [] and len(mem.recente) == 1     # 96 - 0 nao e "mais de" 96
    virar_dia(mem)
    assert mem.consolidar(P.janela_rec + 1)["esquecidos"] == [0] and mem.recente == []
    desligada = M.Memoria(CONFIG_MUNDO_LIGADA)
    assert desligada.consolidar(5) is None and not hasattr(desligada, "duradoura")


def test_t_me_3_a_central_pede_repeticao_e_o_forte_unico_nao_entra():
    mem = nova()
    for k in range(P.n_rep_central + 1):                                         # o 1.o ganha rep = n_rep_central
        guardar(mem, 300, decisao=k, ponto=(40, 72))
    unico = guardar(mem, S, decisao=9, ponto=(900, 900), unid=unidade(("brincar", "bola", 3), BOLA), objetos=[BOLA])
    virar_dia(mem)
    reg = mem.consolidar(500)
    assert [e["id"] for e in mem.central] == [0] and mem.central[0]["memoria"] == "central" and reg["subiram"]["central"] == [0]
    assert unico in {e["id"] for e in mem.duradoura} and all(e["id"] != unico for e in mem.central)
    assert mem.central[0]["rep"] == P.n_rep_central


def test_t_me_3_a_central_tem_um_por_categoria_e_no_maximo_n_cen():
    mem = nova()
    k = 0
    for c in range(P.n_cen + 2):                                                 # n_cen + 2 categorias, cada uma com 3 episodios iguais
        for _ in range(3):
            mem.codificar_autobio({**episodio(r_n=200 + 20 * c), "ponto": (40, 72), "decisao": k, "categoria": [f"acao{c}", "a", 1]})
            k += 1
    virar_dia(mem)
    mem.consolidar(1000)
    cats = [tuple(e["categoria"]) for e in mem.central]
    assert len(cats) == len(set(cats)) == P.n_cen
    fora = [mem.peso(e) for e in mem.duradoura if e["rep"] >= P.n_rep_central]
    assert fora and max(fora) <= min(mem.peso(e) for e in mem.central)           # as de maior peso ficaram
    assert {c[0] for c in cats} == {f"acao{c}" for c in range(2, P.n_cen + 2)}


def test_t_me_3_quem_sai_da_central_volta_a_duradoura_e_o_mais_forte_a_substitui():
    mem = nova()
    for k in range(3):
        guardar(mem, 200, decisao=k)
    virar_dia(mem)
    mem.consolidar(1000)
    velho = mem.central[0]["id"]
    for k in range(10, 14):                                                      # a mesma categoria, mais forte e repetida
        guardar(mem, 800, decisao=k + 1000)
    virar_dia(mem)
    reg = mem.consolidar(3000)
    assert len(mem.central) == 1 and mem.central[0]["sigma"] == 800 and reg["voltaram"] == [velho]
    assert next(e for e in mem.duradoura if e["id"] == velho)["memoria"] == "duradoura"


def test_t_me_3_a_duradoura_cheia_descarta_o_de_menor_peso_e_registra():
    mem = nova()
    for i in range(P.n_dur + 4):
        mem.duradoura.append({**episodio(r_n=P.theta_dur + i), "id": 1000 + i, "lugar": [i, 99], "ponto": [i, 0], "decisao": 0,
                              "memoria": "duradoura"})
    virar_dia(mem)
    reg = mem.consolidar(5000)
    assert len(mem.duradoura) == P.n_dur and reg["por_capacidade"]["duradoura"] == [1000, 1001, 1002, 1003]
    assert min(e["sigma"] for e in mem.duradoura) == P.theta_dur + 4


def test_t_me_3_a_recente_cheia_descarta_pelo_peso_com_a_repeticao():
    mem = nova()
    for k in range(P.n_rec):
        guardar(mem, 200, decisao=k, ponto=(k * 10_000, 0))
    guardar(mem, 200, decisao=50, ponto=(0, 0))                                  # repete o 0: rep = 1, peso maior; sai o 1 (o mais antigo)
    assert mem.saidas_autobio == [{"id": 1, "sigma": 200}] and 0 in {e["id"] for e in mem.recente}


def test_t_me_3_o_peso():
    mem = nova()
    guardar(mem, 150)
    e = mem.recente[0]
    assert mem.peso(e) == 150
    e["rep"], e["rec"] = 2, 4
    assert mem.peso(e) == (150 * 3 * S) // S == 450
    e["sigma"] = -S
    assert mem.peso(e) == S


def test_t_me_3_na_vida_as_memorias_respeitam_as_capacidades_e_o_replay():
    for semente in (101, 303):
        motor, reg = _viver(semente, "comedouro")
        c = orq.cerebro_de(reg)
        mem = c.m.mem
        todos = mem._guardados()
        assert len({e["id"] for e in todos}) == len(todos)                      # cada episodio em uma so memoria
        assert len(mem.recente) <= P.n_rec and len(mem.duradoura) <= P.n_dur and len(mem.central) <= P.n_cen
        cats = [tuple(e["categoria"]) for e in mem.central]
        assert len(cats) == len(set(cats)) and all(e["rep"] >= P.n_rep_central for e in mem.central)
        assert all(e["memoria"] == n for n, ml in (("recente", mem.recente), ("duradoura", mem.duradoura), ("central", mem.central))
                   for e in ml)
        assert sum(e["rec"] for e in todos) <= mem.lembrancas and mem.lembrancas > 0
        assert len(mem.consolidacoes) == mem.dia_consolidado >= 1 or len(mem.consolidacoes) >= 1
        assert [m["lembranca"]["recuperado"] for m in c.motivos if m["lembranca"]["recuperado"] is not None]
        orq.conferir_replay(motor, _viver.fab[1], semente, motor.log.para_jsonl())


# ------------------------------------------------------------------ T-ME-4: o termo da lembranca e a sonda contrafactual
def unid_com(chave, inato, lembranca=0) -> dict:
    """uma unidade sintetica da lista de agora, com o termo `lembranca`"""
    termos = {"inato": inato, "prox": 0, "nov": 0, "incentivo": 0, "habito": 0, "memoria": 0, "persistencia": 0, "lembranca": lembranca}
    soma = sum(termos.values())
    return {**unidade(chave), "termos": termos, "soma": soma, "a": max(0, min(soma, P.a_max))}


def lembrar_de(mem, r_n, objetos=(), **kw):
    """guarda o episodio e devolve o termo da M4 do que a lembranca traz (ou None)"""
    guardar(mem, r_n, objetos=objetos, **kw)
    return mem.termo_lembranca(mem.lembrar(pista(objetos=objetos)))


COMER_9 = ("comer", "podre", 9)
VAGAR = ("explorar", "vagar", None)
ENERGIA = {"leitura": {"energia": S}}


def test_t_me_4_w_lem_e_a_metade_do_w_mem_e_esta_decidido():
    assert P.w_lem == S // 2 == P.w_mem // 2 and PARAMETROS_DIGIBRAIN_INATOS["w_lem"][0] == "DECIDIDO"
    assert "w_lem" in CAMPOS_POR_MODULO["mem"]


def test_t_me_4_o_termo_e_mul_w_lem_sigma_so_na_unidade_da_mesma_acao():
    mem = nova()
    podre = {**COMIDA, "id": 9, "tipo": "podre", "classe": "podre"}
    termo = lembrar_de(mem, -400, objetos=[podre], unid=unidade(COMER_9, podre), comeu="podre")
    assert termo["L"] == M.mul(P.w_lem, -400, S) == -200
    assert mem.casa(termo, unidade(COMER_9, podre))
    assert mem.casa(termo, unidade(("comer", "podre", 31), {**podre, "id": 31}))      # outro objeto da mesma classe de alvo
    assert not mem.casa(termo, unidade(("comer", "a", 7), COMIDA)) and not mem.casa(termo, unidade(VAGAR))
    sem = nova()
    guardar(sem, 300, objetos=[COMIDA])
    assert sem.termo_lembranca(sem.lembrar(pista(pos=(900, 900), objetos=[BOLA], noite=S, fome=900))) is None   # sem lembranca, sem termo


def test_t_me_4_a_visita_so_chega_ao_mesmo_lugar_e_o_sem_alvo_vale_o_comportamento():
    mem = nova()
    termo = lembrar_de(mem, 0, unid=unidade(("explorar", "ponto", (40, 72))), chegou=True, r_ida=-300)
    assert termo["L"] == M.mul(P.w_lem, -300, S) == -150
    assert mem.casa(termo, unidade(("explorar", "ponto", (41, 73)))) and not mem.casa(termo, unidade(("explorar", "ponto", (900, 900))))
    assert not mem.casa(termo, unidade(VAGAR)) and not mem.casa(termo, unidade(("comer", "cheiro", None)))
    mem = nova()
    termo = lembrar_de(mem, -300, depois=leituras(dor=900))                          # o evento sem alvo: o comportamento
    assert termo["so_comportamento"] and mem.casa(termo, unidade(("ocioso", None, None))) and not mem.casa(termo, unidade(VAGAR))


def test_t_me_4_a_sonda_mostra_a_troca_quando_a_lembranca_muda_a_escolha():
    arb = Arbitragem(autobio=True)
    # o L = -300 tira o comer podre de 500 para 200; com u = 0,5 (T = 700, alvo 350) cai no vagar, e sem o L (500/500, alvo 500) no vagar...
    us = [unid_com(COMER_9, 500, -300), unid_com(VAGAR, 500)]
    out = arb.escolher(us, {"g_exp": 0}, ENERGIA, RngContada(0.6))                    # alvo 420: com o L, vagar; sem o L (T = 1000, alvo 600), vagar
    assert out["unidade"]["acao"] == "explorar" and out["sondas"]["lembranca_decidiu"] is False
    out = arb.escolher(us, {"g_exp": 0}, ENERGIA, RngContada(0.4))                    # alvo 280: com o L (comer 200), vagar; sem o L, comer
    assert out["unidade"]["acao"] == "explorar" and out["sondas"]["sem_lembranca"] == list(COMER_9)
    assert out["sondas"]["lembranca_decidiu"] is True and out["sondas"]["memoria_decidiu"] is True    # sem_memoria tira o L
    assert out["sondas"]["sem_memoria"] == out["sondas"]["sem_lembranca"] and out["sondas"]["aprendido_decidiu"] is True
    assert out["sondas"]["incentivo_decidiu"] is False and out["sondas"]["habito_decidiu"] is False


def test_t_me_4_a_sonda_nao_mostra_troca_quando_a_lembranca_nao_muda_a_escolha():
    arb = Arbitragem(autobio=True)
    us = [unid_com(COMER_9, 900, -100), unid_com(VAGAR, 0)]                           # so o comer concorre
    out = arb.escolher(us, {"g_exp": 0}, ENERGIA, RngContada())
    assert out["unidade"]["acao"] == "comer" and out["sondas"]["lembranca_decidiu"] is False
    assert out["sondas"]["sem_lembranca"] == list(COMER_9) and out["sondas"]["memoria_decidiu"] is False
    sem_termo = [unid_com(COMER_9, 500), unid_com(VAGAR, 500)]                        # L = 0: a sonda e a decisao
    for u in (0.1, 0.5, 0.9):
        out = arb.escolher(sem_termo, {"g_exp": 0}, ENERGIA, RngContada(u))
        assert out["sondas"]["lembranca_decidiu"] is False and out["sondas"]["sem_lembranca"] == out["sondas"]["sem_memoria"]


def test_t_me_4_a_sonda_nao_consome_a_rng_de_politica_nem_muda_o_estado():
    arb = Arbitragem(autobio=True)
    us = [unid_com(COMER_9, 500, -300), unid_com(VAGAR, 500)]
    antes = copy.deepcopy(us)
    rng = RngContada(0.4)
    arb.escolher(us, {"g_exp": 0}, ENERGIA, rng)
    assert rng.n == 1 and us == antes and arb.sorteios == 1                           # so a chamada do sorteio; as unidades intactas
    rng = RngContada()
    arb.escolher([unid_com(COMER_9, 500), unid_com(VAGAR, 0)], {"g_exp": 0}, ENERGIA, rng)
    assert rng.n == 0                                                                 # um candidato so: nenhuma chamada, sonda inclusa
    reflexo = arb.escolher(us + [unid_com(("dormir", None, None), 0)], {"g_exp": 0}, {"leitura": {"energia": 0}}, RngContada())   # o reflexo: nenhuma sonda decide
    assert not any(v for k, v in reflexo["sondas"].items() if k.endswith("_decidiu"))


def test_t_me_4_desligada_as_sondas_sao_as_de_hoje():
    assert set(Arbitragem().sondas) == {"sem_incentivo", "sem_habito", "sem_memoria", "sem_persistencia", "sem_afeto", "so_inato"}
    assert Arbitragem().sondas["sem_memoria"] == ("memoria",)
    ligada = Arbitragem(autobio=True)
    assert ligada.sondas["sem_lembranca"] == ("lembranca",) and ligada.sondas["sem_memoria"] == ("memoria", "lembranca")
    assert "lembranca" in ligada.sondas["so_inato"]


@pytest.mark.parametrize("semente", SEMENTES)
def test_t_me_4_na_vida_o_termo_a_sonda_e_o_replay(semente):
    motor, reg = _viver(semente)
    orq.conferir_replay(motor, _viver.fab[1], semente, motor.log.para_jsonl())      # G1: o replay bit a bit com a chave ligada
    c = orq.cerebro_de(reg)
    assert all("lembranca" in x["termos"] for m in c.motivos for x in m["unidades"])
    for m in c.motivos:
        lem = m["lembranca"]
        assert "lembranca_decidiu" in m["sondas"] and "sem_lembranca" in m["sondas"]
        assert (lem["L"] is None) == (lem["recuperado"] is None)
        assert all(x["chave"] in lem["unidades"] for x in m["unidades"] if x["termos"]["lembranca"] != 0)
        if not lem["unidades"] or lem["L"] == 0:                                    # sem unidade que a receba ou L = 0, a sonda nao troca
            assert m["sondas"]["lembranca_decidiu"] is False
        if m["sondas"]["lembranca_decidiu"]:
            assert m["sondas"]["sem_lembranca"] != m["escolha"]
    assert c.m.arb.sorteios <= len(c.motivos)


# ------------------------------------------------------------------ as vidas: G1, G2-SEPARADO, T-ME-0 e T-ME-1 no replay
def _viver(semente: int, lugar: str = "longe_fixo", dono: str = "relapso", ligada: bool = True):
    original = orq.config_do_braco
    orq.config_do_braco = lambda b, g=None, c=False: replace(original(b, g, c), memoria_autobio=ligada)
    try:
        motor, reg, fab = orq.viver("M3", dono, lugar, semente, 3, 16, conserto=True)
    finally:
        orq.config_do_braco = original
    _viver.fab = (motor, fab)
    return motor, reg


@pytest.mark.parametrize("semente", SEMENTES)
def test_g1_o_replay_com_a_subchave_ligada_e_o_mesmo_log_da_desligada(semente):
    motor, reg = _viver(semente)
    orq.conferir_replay(motor, _viver.fab[1], semente, motor.log.para_jsonl())   # o estado interno, com a recente, bit a bit
    orq.conferir_mecanismo("M3", reg, None)
    orq.conferir_cenario(motor, reg)
    c = orq.cerebro_de(reg)
    assert c.cd.memoria_autobio and all("autobio" in m["consequencia"] for m in c.motivos if m["consequencia"])
    assert c.m.mem.estado_interno()["autobio"]["proximo_id"] > 0
    # na M2 o lugar lembrado vale pela soma (MA-2): a vida pode divergir da desligada; a rng de politica segue so a do M-ARB
    assert c.m.arb.sorteios <= len(c.motivos)
    # a referencia ao log: o tick do episodio e o da decisao (k x o intervalo, a Observacao do Registro)
    assert all(e["tick"] == e["decisao"] * 15 for e in c.m.mem.estado_interno()["autobio"]["recente"])


def test_t_me_1_o_mesmo_log_codifica_os_mesmos_episodios(monkeypatch):
    todos: list = []
    original = M.Memoria.codificar_autobio
    monkeypatch.setattr(M.Memoria, "codificar_autobio", lambda self, ep: (todos.append(json.dumps(ep, sort_keys=True)),
                                                                            original(self, ep))[1])
    motor, _ = _viver(202, "comedouro")
    n = len(todos)
    assert n > 0
    orq.conferir_replay(motor, _viver.fab[1], 202, motor.log.para_jsonl())
    assert todos[n:] == todos[:n]                                                # o replay codificou os mesmos, na mesma ordem


def test_t_me_1_a_visita_vazia_na_vida_tem_o_custo_da_ida(monkeypatch):
    todos: list = []
    original = M.Memoria.codificar_autobio
    monkeypatch.setattr(M.Memoria, "codificar_autobio", lambda self, ep: (todos.append(ep), original(self, ep))[1])
    _, reg = _viver(101, "comedouro")
    c = orq.cerebro_de(reg)
    visitas = [e for e in todos if e["origem"] == "visita"]
    assert visitas
    for e in visitas:
        m = c.motivos[e["decisao"]]
        assert m["consequencia"]["chegou"] and m["consequencia"]["comeu"] is None and m["escolha"][1] == "ponto"
        ida = next(f["r"] for f in m["fins"] if f["chave"] == m["escolha"])
        assert e["sigma"] == min(0, ida) and e["categoria"][2] == (e["sigma"] < 0) * -1
    # todo consumo vira episodio de consumo; nenhuma decisao sem consumo nem visita vira episodio sem passar o limiar
    consumos = [m for m in c.motivos if m["consequencia"] and m["consequencia"]["comeu"] is not None]
    assert len([e for e in todos if e["origem"] == "consumo"]) == len(consumos)
    for e in todos:
        if e["origem"] == "evento":
            subida = max(e["delta"][r] for r in M.AFETIVOS)
            assert abs(e["sigma"]) >= P.theta_sig or subida >= P.theta_sig


def test_g2_separado_ligada_muda_so_a_vida_do_braco_que_a_liga():
    desligada = orq.viver("M3", "relapso", "longe_fixo", 101, 3, 16, conserto=True)
    ligada = _viver(101)
    estado = lambda v: json.dumps(orq.cerebro_de(v[1]).estado_interno(), sort_keys=True)   # noqa: E731
    assert estado(desligada) != estado(ligada)
    assert estado(desligada) == estado(orq.viver("M3", "relapso", "longe_fixo", 101, 3, 16, conserto=True))
    m2 = orq.viver("M2", "relapso", "longe_fixo", 101, 3, 16, conserto=True)
    assert orq.cerebro_de(m2[1]).cd.memoria_autobio is False and "autobio" not in orq.cerebro_de(m2[1]).m.mem.estado_interno()


def test_g2_separado_nada_fora_do_pacote_le_a_chave():
    donos_da_chave = {"digilab/config.py", "digilab/digibrain/adapt.py", "digilab/digibrain/impulso.py", "digilab/digibrain/mem.py"}
    achados = set()
    for pasta in ("digilab", "experiments", "web", "tools", "servidor", "digilab_fala_livre"):
        if not (RAIZ / pasta).exists():
            continue
        for f in (RAIZ / pasta).rglob("*"):
            if f.suffix in (".py", ".ts", ".tsx", ".js") and "node_modules" not in f.parts and "memoria_autobio" in f.read_text(
                    encoding="utf-8", errors="ignore"):
                achados.add(f.relative_to(RAIZ).as_posix())
    assert achados == donos_da_chave


# ------------------------------------------------------------------ G-MECANISMO, G-INT, G-SEM-DIRECAO, G-RECEPTOR
SUBSTITUIDOS_PELA_SOMA = {"test_t_mem_2_a_recuperacao", "test_t_mem_4_a_visita_vazia_apaga_o_lugar", "test_t_motivo_1_os_termos_e_as_sondas"}
_DE_HOJE = [n for n, f in inspect.getmembers(tm, inspect.isfunction) if n.startswith("test_")]


@pytest.mark.parametrize("nome", _DE_HOJE)
def test_g_mecanismo_os_de_hoje_com_a_subchave_ligada(nome, monkeypatch):
    """cada teste de mecanismo de hoje (tests/test_digibrain_mecanismo.py) com as duas subchaves do cheiro e a `memoria_autobio`; o M-MEM
    que um teste monta a mao e poe no cerebro (o T-MOTIVO-1) nasce com a recente, como o do cerebro ligado (sem ela, o relogio falha alto).
    **Os tres que montam o lugar lembrado por `codificar` (a lista de hoje) ficam de fora:** com a subchave o valor do lugar e a soma dos
    episodios das tres memorias (MA-2, decidida), nao a lista de hoje; o equivalente de cada um, com a soma, esta nos T-ME-2"""
    if nome in SUBSTITUIDOS_PELA_SOMA:
        pytest.skip("o lugar lembrado pela lista de hoje; com a subchave vale a soma (MA-2), nos T-ME-2")
    monkeypatch.setattr(tm, "CONFIG_DIGIBRAIN_LIGADA", LIGADA)
    monkeypatch.setattr(tm, "Memoria", lambda cm, inatos=None: M.Memoria(cm, inatos, autobio=True))
    getattr(tm, nome)()


def test_g_int_e_g_receptor_as_intencoes_e_os_receptores_de_hoje_na_vida_ligada():
    c = orq.cerebro_de(_viver(505)[1])
    fins = c.m.estado.fins
    assert set(fins) == set(orq.fins_do_estado("M3")) and fins["meta"] > 0
    assert all(set(m["afeto"]["urgencias"]) == set(c.m.sens.receptores) for m in c.motivos)
