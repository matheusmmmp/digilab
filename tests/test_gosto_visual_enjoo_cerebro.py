"""O enjoo da imagem no corpo e no cerebro do Python (GOSTO_VISUAL; docs/registro/2026-11.md, D-GV-ENJOO-PY-1 a 3 e D-GV-ENJOO-CER-1...;
a ConfigEnjooTela, desligada por padrao).

- a config: desligada, o status de cada campo, a falha alto, as k das meias-vidas, a chave so com a tela (corpo) e com o olhar (cerebro);
- o corpo: a habituacao presa ao estimulo (sem olhar, ela nao volta em 1 h), a novidade no comeco de cada olhar cai e o enjoo sobe a cada
  olhar (o pet olha em rajadas de uma decisao, o padrao do diagnostico com as midias reais, D-GV-VIDEO-9 a 13), trocar de programa devolve a
  novidade e o interesse, voltar ao anterior logo depois nao desenjoa, o prototipo parado (sem o "enjoo migrante" do P0);
- a sonda (os perfis A e B das duas TVs): a novidade nos dois sentidos, sem o susto de comecar a olhar, e o estresse do B (o da GV-17);
- o cerebro: o U invertido do agrado (a exposicao satura e vira tedio), o termo `enjoo` na unidade de olhar, a imagem parada que enjoa ao
  longo dos olhares, trocar de imagem que devolve o interesse;
- o replay igual, a chave desligada byte a byte (o gabarito de antes) e o determinismo sem rng nova.
Sementes: as dos testes (101 a 505).
"""
from __future__ import annotations

import ast
import copy
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

import gabarito_gosto_visual_enjoo as G  # noqa: E402
import sonda_duas_tvs as sd  # noqa: E402

from digilab import corpo as corpo_mod  # noqa: E402
from digilab.config import (CANAIS_TELA, CONFIG_CORPO_DRIVES, CONFIG_ENJOO_TELA, CONFIG_ENJOO_TELA_LIGADA, CONFIG_MUNDO_LIGADA,  # noqa: E402
                            CONFIG_OLHAR, CONFIG_PADRAO, PARAMETROS_ENJOO_TELA, ConfigEnjooTela, ConfigTela)
from digilab.corpo import RECEPTOR_ENJOO_TELA, RECEPTOR_NOVIDADE_TELA, Corpo, div_arred, k_meia_vida  # noqa: E402
from digilab.digibrain import sens as sens_mod  # noqa: E402
from digilab.digibrain.sens import Sens  # noqa: E402
from digilab.genoma_visao import GenomaVisao  # noqa: E402
from digilab.motor_corpo import PercepcaoCorpo  # noqa: E402
from digilab.mundo import reproduzir_mundo  # noqa: E402
from digilab.state import Estado  # noqa: E402

S = 1024
C = 450000
TELA = ConfigTela(ligada=True)
CC = CONFIG_CORPO_DRIVES
LIGADA = CONFIG_ENJOO_TELA_LIGADA
SEMENTES = (101, 202, 303, 404, 505)
A = dict(zip(CANAIS_TELA, sd.PERFIL_A))                      # o perfil calmo da sonda (0,2 C em todo canal)
B = dict(zip(CANAIS_TELA, sd.PERFIL_B))                      # o agitado (0,8 C)
ZERO = dict.fromkeys(CANAIS_TELA, 0)
OUTRO = dict(zip(CANAIS_TELA, (C // 2, C // 5, C // 2, 4 * C // 5, C // 5, C // 2, C // 5)))   # longe dos dois


def corpo(ce: ConfigEnjooTela | None = LIGADA) -> Corpo:
    return Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, com_mundo=True, cfg_tela=TELA, cfg_enjoo_tela=ce)


def ticks(c: Corpo, estimulo: dict, n: int, t0: int = 0) -> None:
    for t in range(n):
        c.sentir_tela(dict(estimulo))
        c.passo(Estado(tick=t0 + t))


def ler(c: Corpo, estimulo: dict) -> dict:
    """os receptores da tela com o estimulo de agora (a percepcao, sem andar o tick)"""
    c.sentir_tela(dict(estimulo))
    return c.leituras_tela()


# ================================================================== a config
def test_a_config_nasce_desligada_com_status_e_k():
    assert not CONFIG_ENJOO_TELA.ligada and LIGADA.ligada
    assert set(PARAMETROS_ENJOO_TELA) == {f.name for f in fields(ConfigEnjooTela)}
    assert all(st == "PROPOSTO" and "SEM FONTE" in fonte for st, fonte in PARAMETROS_ENJOO_TELA.values())
    for k, h in (("k_desenjoo", "meia_vida_desenjoo"), ("k_olhando", "meia_vida_olhando"), ("k_enjoo", "meia_vida_enjoo")):
        assert getattr(LIGADA, k) == k_meia_vida(getattr(LIGADA, h), CC.bits_meia_vida)
    assert sens_mod.RECEPTOR_ENJOO_TELA == RECEPTOR_ENJOO_TELA
    # o receptor novo fica antes dos da tela (que fecham a PercepcaoCorpo) e nasce None
    campos = [f.name for f in fields(PercepcaoCorpo)]
    assert campos.index(RECEPTOR_ENJOO_TELA) < campos.index("tela_cor")
    assert RECEPTOR_ENJOO_TELA not in corpo(None).receptores() and RECEPTOR_ENJOO_TELA in corpo().receptores()


@pytest.mark.parametrize("kw", [{"ligada": 1}, {"meia_vida_desenjoo": 0}, {"prototipos": 0}, {"raio_mesmo": -1}, {"w_enjoo": S + 1},
                                {"peso_tedio": -1}, {"saturacao_exposicao": S}, {"tau_enjoo_lembrado": 14}, {"k_enjoo": 1.5}])
def test_a_config_falha_alto(kw):
    with pytest.raises((ValueError, TypeError)):
        ConfigEnjooTela(**kw)


def test_a_chave_so_com_a_tela_e_com_o_olhar():
    with pytest.raises(ValueError, match="k_enjoo"):
        corpo(replace(LIGADA, k_enjoo=2961))
    with pytest.raises(ValueError, match="ConfigTela"):
        Corpo.de_estado(Estado(), CONFIG_PADRAO, CC, com_mundo=True, cfg_enjoo_tela=LIGADA)
    from digilab.config import CONFIG_DIGIBRAIN_LIGADA
    from digilab.digibrain import DigiBrain
    with pytest.raises(ValueError, match="olhar"):
        DigiBrain(CONFIG_PADRAO, CONFIG_DIGIBRAIN_LIGADA, CONFIG_MUNDO_LIGADA, semente=101, cfg_enjoo_tela=LIGADA)
    with pytest.raises(ValueError, match="olhar"):
        Sens(CONFIG_PADRAO, CONFIG_MUNDO_LIGADA, enjoo=LIGADA)


# ================================================================== o corpo: a habituacao presa ao estimulo e a memoria curta
def test_sem_olhar_a_habituacao_nao_volta_em_uma_hora():
    on, off = corpo(), corpo(None)
    for c in (on, off):
        ticks(c, A, 15)
        ticks(c, ZERO, 60, 15)
    adapt = [f"adaptacao_tela_{k}" for k in CANAIS_TELA]
    # desligada, a adaptacao some (meia-vida de 60) e a mesma imagem volta a ser novidade; ligada, ela fica (meia-vida de 720)
    assert all(on.q[a] > 3 * off.q[a] for a in adapt)
    assert ler(on, A)[RECEPTOR_NOVIDADE_TELA] < ler(off, A)[RECEPTOR_NOVIDADE_TELA] // 2
    assert ler(on, A)[RECEPTOR_ENJOO_TELA] > S // 3                  # e o enjoo dela fica


def test_em_rajadas_de_uma_decisao_a_novidade_cai_e_o_enjoo_sobe():
    """o padrao do diagnostico com as midias reais (D-GV-VIDEO-9 a 13): um olhar de 15 ticks a cada ~5 h. No comeco de cada olhar, ligada a
    chave, a novidade da mesma imagem cai e o enjoo dela sobe; desligada, a novidade volta inteira e nao ha enjoo"""
    for ce in (LIGADA, None):
        c, t = corpo(ce), 0
        nov, enj = [], []
        for _ in range(5):
            r = ler(c, A)
            nov.append(r[RECEPTOR_NOVIDADE_TELA])
            enj.append(r.get(RECEPTOR_ENJOO_TELA))
            ticks(c, A, 15, t)
            ticks(c, ZERO, 300, t + 15)
            t += 315
        if ce is None:
            assert max(nov) - min(nov) <= 2 and nov[0] > S // 2 and set(enj) == {None}     # volta inteira (o arredondamento)
        else:
            assert nov[0] > S // 2 and all(b < a for a, b in zip(nov, nov[1:])) and nov[-1] < nov[0] // 2
            # o enjoo sobe a cada olhar ate ~0,6 S, o equilibrio de um olhar a cada 5 h com a meia-vida de 720
            assert enj[0] == 0 and all(b > a for a, b in zip(enj, enj[1:])) and enj[-1] > LIGADA.saturacao_exposicao


def test_trocar_de_programa_devolve_a_novidade_e_o_interesse():
    c = corpo()
    ticks(c, A, 60)
    r = ler(c, OUTRO)
    assert r[RECEPTOR_ENJOO_TELA] == 0 and r[RECEPTOR_NOVIDADE_TELA] > c.ct.corte_novidade
    assert len(c.memoria_tela) == 1                             # o perfil novo ainda nao nasceu: nasce no tick
    ticks(c, OUTRO, 1, 60)
    assert len(c.memoria_tela) == 2


def test_voltar_ao_programa_anterior_logo_depois_nao_desenjoa():
    c = corpo()
    ticks(c, A, 60)
    antes = ler(c, A)[RECEPTOR_ENJOO_TELA]
    ticks(c, B, 60, 60)
    volta = ler(c, A)
    assert antes > 9 * S // 10
    assert volta[RECEPTOR_ENJOO_TELA] > 9 * antes // 10        # a memoria lembra o A (so a meia-vida do desenjoo andou)
    assert volta[RECEPTOR_NOVIDADE_TELA] > 0                    # a adaptacao, que estava no B, ve a mudanca


def test_o_prototipo_fica_parado_e_a_memoria_e_curta():
    """sem o "enjoo migrante" do P0 (D-GV-VIDEO): a cena perto cai no mesmo prototipo, mas o prototipo nao anda para ela"""
    c = corpo()
    perto = {k: v + 27000 for k, v in A.items()}                 # a variacao de uma cena da grade
    ticks(c, A, 5)
    ticks(c, perto, 30, 5)
    assert [p for p, _ in c.memoria_tela] == [tuple(A[k] for k in CANAIS_TELA)]
    # a memoria cheia: o perfil novo toma o lugar do menos enjoado (no empate, o mais antigo) e vai para o fim
    c = corpo()
    perfis = [dict.fromkeys(CANAIS_TELA, i * 70000) for i in range(1, 7)]
    for i, p in enumerate(perfis):
        ticks(c, p, 1 + 10 * (i == 0), 20 * i)                  # o primeiro, mais olhado
    assert len(c.memoria_tela) == LIGADA.prototipos
    menos = min(range(6), key=lambda i: (c.memoria_tela[i][1], i))
    some = c.memoria_tela[menos][0]
    ticks(c, OUTRO, 1, 500)
    assert len(c.memoria_tela) == 6 and some not in [p for p, _ in c.memoria_tela]
    assert c.memoria_tela[-1][0] == tuple(OUTRO[k] for k in CANAIS_TELA)
    d = c.para_dict()["tela"]
    assert set(d) == {"estimulo", "sentido", "memoria", "volume_visto"} and len(d["memoria"]) == 6
    assert set(corpo(None).para_dict()["tela"]) == {"estimulo", "sentido"}   # desligada, o estado de hoje


# ================================================================== a sonda: a novidade, o susto e o estresse
def test_a_novidade_conta_nos_dois_sentidos():
    for ce, simetrica in ((LIGADA, True), (None, False)):
        ab, ba = corpo(ce), corpo(ce)
        ticks(ab, A, 120)
        ticks(ba, B, 120)
        n_ab, n_ba = ler(ab, B)[RECEPTOR_NOVIDADE_TELA], ler(ba, A)[RECEPTOR_NOVIDADE_TELA]
        if simetrica:
            assert n_ab == n_ba > TELA.corte_novidade
        else:
            assert n_ab > TELA.corte_novidade and n_ba == 0           # o efeito 1 da D-GV-ENJOO-PY-2, desligada


def test_comecar_a_olhar_nao_da_susto_so_porque_o_estimulo_de_antes_era_zero():
    on, off = corpo(), corpo(None)
    for c in (on, off):
        c.sentir_tela(ZERO)
        c.sentir_tela(B)
    assert on.q["susto"] == 0 and off.q["susto"] == TELA.susto_salto     # o efeito 2, desligada
    # ligada: o salto e contra o ultimo estimulo visto, mesmo com uma pausa no meio (A, nada, B e um salto de verdade)
    c = corpo()
    ticks(c, A, 5)
    ticks(c, ZERO, 100, 5)
    c.sentir_tela(B)
    assert c.q["susto"] == TELA.susto_salto
    c.sentir_tela(B)                                            # o mesmo de novo: nada
    assert c.q["susto"] == TELA.susto_salto


def test_o_estresse_do_b_e_o_da_gv17_e_nao_muda_com_a_chave():
    """o efeito 3 fica justificado (D-GV-ENJOO-CER-7): o B tem o volume e o movimento acima de 3C/4, e a GV-17 decidiu que o som alto e o
    movimento demais estressam. Com conteudo real, o diagnostico (D-GV-VIDEO) nunca passou do corte"""
    for ce in (LIGADA, None):
        a, b = corpo(ce), corpo(ce)
        ticks(a, A, 1)
        ticks(b, B, 1)
        assert a.q["estresse"] == 0
        assert b.q["estresse"] == corpo_mod.passo_meia_vida(div_arred(2 * (B["volume"] - TELA.estresse_corte), TELA.estresse_divisor),
                                                            CC.k_meia_vida_estresse)


# ================================================================== o cerebro: o U invertido e o termo enjoo
def _sens() -> Sens:
    g = GenomaVisao(dict.fromkeys(CANAIS_TELA, C // 2), dict.fromkeys(CANAIS_TELA, C // 4))
    return Sens(CONFIG_PADRAO, CONFIG_MUNDO_LIGADA, olhar=replace(CONFIG_OLHAR, tau_exposicao=60), genoma=g, enjoo=LIGADA)


def test_o_u_invertido_do_agrado():
    s = _sens()
    niveis = dict.fromkeys(CANAIS_TELA, 3 * S // 4)              # um quarto da escala acima do otimo: agrada pouco no comeco
    curva, deslocs = [], []
    for passo in range(17):
        e = min(S, passo * 64)                                    # o enjoo sobe a cada olhar
        curva.append(s.agrado_efetivo(niveis, e))
        s.expor(niveis, e)
        deslocs.append(s.desloc["cor"])
    pico_ = max(range(len(curva)), key=lambda i: curva[i])
    assert 0 < pico_ < len(curva) - 1 and curva[pico_] > curva[0] and curva[pico_] > curva[-1]
    # a exposicao para na saturacao (enjoo >= S/2: passo 8 em diante)
    assert deslocs[8] == deslocs[-1] and deslocs[7] > deslocs[0]
    assert s.tedio(S // 2) == 0 and s.tedio(S) == LIGADA.peso_tedio
    with pytest.raises(ValueError):
        s.agrado_efetivo(niveis, S + 1)


def _por_dia(m, dias: int) -> list[int]:
    ms = m.politica.motivos
    return [sum(1 for x in ms[d * 96:(d + 1) * 96] if x["acao"] != "dormir" and x["olhar"]["olha"] is not None) for d in range(dias)]


@pytest.fixture(scope="module")
def paradas():
    return {(s, ce is not None): G.viver_parada(s, 3, cfg_enjoo_tela=ce) for s in SEMENTES for ce in (LIGADA, None)}


def test_a_imagem_parada_enjoa_ao_longo_dos_olhares(paradas):
    """o pet olha pouco (de 0 a 5 olhares por dia, D-GV-VIDEO): em vez da fracao de cada dia, o enjoo lido em cada olhar e o termo dele"""
    for s in SEMENTES:
        m = paradas[(s, True)]
        lidos = [x["olhar"]["enjoo"] for x in m.politica.motivos if x["olhar"]["enjoo"] is not None]
        if len(lidos) >= 2:
            assert lidos[-1] > lidos[0] >= S // 2                 # um olhar ja leva o enjoo a metade; os seguintes sobem
        termos = [u["termos"]["enjoo"] for x in m.politica.motivos for u in x["unidades"] if u["chave"][0] == "olhar"]
        assert all(t <= 0 for t in termos) and (not lidos or min(termos) < 0)
        assert all("enjoo" not in u["termos"] for x in paradas[(s, False)].politica.motivos for u in x["unidades"])
    on = sum(sum(_por_dia(paradas[(s, True)], 3)) for s in SEMENTES)
    off = sum(sum(_por_dia(paradas[(s, False)], 3)) for s in SEMENTES)
    assert on < off                                              # somadas as cinco sementes, a imagem parada enjoada e menos olhada


def test_trocar_de_imagem_devolve_o_interesse():
    """a mesma vida ate o dia 1, e entao duas copias: uma segue com a imagem, a outra troca; o primeiro enjoo lido depois da troca e o da
    imagem nova (um olhar so), menor que o da imagem velha"""
    m = G.viver_parada(303, 1, cfg_enjoo_tela=LIGADA)
    troca = copy.deepcopy(m)
    troca.sentido_tela("tv", (3, 3, 3, 3, 4, 3, 3))
    n0 = len(m.politica.motivos)
    primeiros = []
    for x in (m, troca):
        for _ in range(48):
            x.avancar(60)
        lidos = [y["olhar"]["enjoo"] for y in x.politica.motivos[n0:] if y["olhar"]["enjoo"] is not None]
        assert lidos, "sem olhar depois da troca"
        primeiros.append(lidos[0])
    assert primeiros[1] < primeiros[0]


# ================================================================== o replay, a chave desligada e o determinismo
def test_o_replay_e_igual_com_a_chave_ligada(paradas):
    m = paradas[(202, True)]
    fp, fm = G.fabricas_parada(202, LIGADA)
    r = reproduzir_mundo(m.log, fp, semente=202, fabrica_motor=fm)
    assert G.impressao(r) == G.impressao(m)
    assert json.dumps(r.corpo.para_dict(), sort_keys=True) == json.dumps(m.corpo.para_dict(), sort_keys=True)


def test_a_chave_desligada_sai_o_gabarito_de_antes_byte_a_byte():
    gravado = json.loads(G.ARQUIVO.read_text(encoding="utf-8"))
    for s in (101, 303):
        assert G.impressao(G.viver_parada(s, cfg_enjoo_tela=CONFIG_ENJOO_TELA)) == gravado[f"parada|{s}"]


def test_determinismo_e_nenhuma_rng_nova(paradas):
    estado = random.getstate()
    m = G.viver_parada(101, 3, cfg_enjoo_tela=LIGADA)
    assert random.getstate() == estado
    assert G.impressao(m) == G.impressao(paradas[(101, True)])
    # o corpo e o M-SENS nao sorteiam: nenhum import de random
    for mod in (corpo_mod, sens_mod):
        arvore = ast.parse(Path(mod.__file__).read_text(encoding="utf-8"))
        nomes = {a.name for n in ast.walk(arvore) if isinstance(n, ast.Import) for a in n.names}
        nomes |= {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom) and n.module}
        assert "random" not in nomes
