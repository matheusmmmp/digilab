"""O cheiro proprio, o rastro e o som, o lado do mundo (dois pets, etapa 8, degrau 1b; docs/TAREFA_V2_DOIS_PETS.md; desenho
docs/futuro/dois_pets.md, secoes 5.3, 5.4 e 5.6; OA-1 a OA-3).

- G2: com a ConfigSentidos desligada, os 84 grupos de tests/gabaritos/sentidos_vidas_de_hoje.json (gravados antes, com o codigo de antes)
  saem byte a byte; com a chave ligada e um pet so, nada e guardado; com a chave ligada e dois pets, os cerebros de hoje (que nao leem os
  sentidos) vivem a mesma vida, e so os registros dos sentidos se somam.
- G-SENTIDOS (cheiro e rastro): a conta inteira do cheiro da comida (a mesma, com outro raio); uma marca por decisao, na posicao da decisao,
  so com os dois pets presentes, ate `max_marcas`, e a marca some na idade T; o cheiro de cada outro, a direcao e as duas narinas, conferidos
  na hora de cada decisao contra uma conta refeita no teste.
- G-SENTIDOS (som): um som por evento (comer, a bola, chamar, emburrar), na posicao do pet; ouvido so a d < R_som, em linha reta, com a
  direcao, a distancia e a intensidade no centro e nos dois ouvidos refeitas no teste; a caixa de cada pet chega inteira a decisao
  seguinte, na ordem, sem os sons do proprio pet.
- G-RECEPTOR-SOCIAL: a `PercepcaoSentidos` so tem numeros e nomes; mudar o estado interno do outro sem mudar onde ele esta e o que faz nao
  muda nada do que se sente dele.
- A geometria das duas posicoes de amostra (a esquerda e a direita da direcao do ultimo passo).
- G1-GRUPO com os sentidos: o replay do texto do registro refaz tudo, e o cabecalho confere a ConfigSentidos.
Sementes: so as dos testes (101, 202, 303).
"""
from __future__ import annotations

import json
import math
import random
import sys
from dataclasses import asdict, fields, replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import gabarito_sentidos as gs  # noqa: E402
from digilab.config import (CONFIG_CORPO_DRIVES, CONFIG_OLFATO, CONFIG_OUVIDO, CONFIG_GRUPO_LIGADA, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, CONFIG_SENTIDOS, CONFIG_SENTIDOS_LIGADA,  # noqa: E402
                            TICKS_POR_DIA, ConfigSentidos)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoPet  # noqa: E402
from digilab.grupo import Grupo, PetDoGrupo, RegistroGrupo, reproduzir_grupo, sementes_do_grupo, simular_grupo  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import (DIR16, ESCALA_DIR, PARAMETROS_SENTIDOS, PASSO_INICIAL, SONS, DonoComLugar, MotorMundo, Mundo, PercepcaoSentidos,  # noqa: E402
                           PercepcaoSocial, campo_em, cheiro_em, direcao_do_campo, direcao_do_cheiro, direcao_em_16, direcao_em_8,
                           div_arred, fontes_do_pet, pontos_laterais, som_ouvido)

CM = gs.gdp.LAYOUTS["padrao"]
CS = CONFIG_SENTIDOS_LIGADA
SUB = CM.sub
DIAS = 3


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


# ================================================================== as contas de referencia (refeitas aqui, sem o codigo do mundo)
def ref_campo(x, y, fontes, raio):
    total = 0
    for fx, fy, a in fontes:
        d = math.isqrt((fx - x) ** 2 + (fy - y) ** 2)
        if d < raio:
            total += a * (raio - d) // raio
    return total


def ref_arred(n, d):
    q, r = divmod(abs(n), d)
    q += 2 * r >= d
    return q if n >= 0 else -q


def ref_direcao(x, y, fontes, raio, sub):
    centro = ref_campo(x, y, fontes, raio)
    melhor, direcao = centro, 0
    for k in range(8):
        cx, cy = DIR16[2 * k]
        c = ref_campo(x + ref_arred(cx * sub, ESCALA_DIR), y + ref_arred(cy * sub, ESCALA_DIR), fontes, raio)
        if c > melhor:
            melhor, direcao = c, k + 1
    return centro, direcao


def ref_laterais(x, y, passo, af):
    """a esquerda e a direcao girada 90 graus no sentido anti-horario (com y para o sul: (hx, hy) -> (hy, -hx)); a direita, o contrario"""
    hx, hy = DIR16[passo]
    esq = (x + ref_arred(hy * af, ESCALA_DIR), y + ref_arred(-hx * af, ESCALA_DIR))
    dir_ = (x + ref_arred(-hy * af, ESCALA_DIR), y + ref_arred(hx * af, ESCALA_DIR))
    return esq, dir_


def ref_fontes(x, y, marcas, tick, cs):
    fontes = [(x, y, cs.olfato.cheiro_pet)]
    for mx, my, t in marcas:
        idade = tick - t
        a = cs.olfato.cheiro_marca * (cs.olfato.idade_marca - idade) // cs.olfato.idade_marca if idade < cs.olfato.idade_marca else 0
        if a > 0:
            fontes.append((mx, my, a))
    return fontes


def ref_cheiro(x, y, passo, fontes, cs, sub):
    raio = cs.olfato.raio_celulas * sub
    centro, direcao = ref_direcao(x, y, fontes, raio, sub)
    esq, dir_ = ref_laterais(x, y, passo, cs.olfato.afastamento_narinas)
    return centro, direcao, ref_campo(*esq, fontes, raio), ref_campo(*dir_, fontes, raio)


def ref_direcao_8(dx, dy):
    if dx == 0 and dy == 0:
        return 0
    produtos = [DIR16[2 * k][0] * dx + DIR16[2 * k][1] * dy for k in range(8)]
    return produtos.index(max(produtos)) + 1


def ref_som(lx, ly, passo, sx, sy, cs, sub):
    raio = cs.ouvido.raio_som_celulas * sub
    d = math.isqrt((sx - lx) ** 2 + (sy - ly) ** 2)
    if d >= raio:
        return None
    a = cs.ouvido.som
    esq, dir_ = ref_laterais(lx, ly, passo, cs.ouvido.afastamento_ouvidos)
    no = lambda px, py: ref_campo(px, py, [(sx, sy, a)], raio)  # noqa: E731
    return ref_direcao_8(sx - lx, sy - ly), d, no(lx, ly), no(*esq), no(*dir_)


# ================================================================== os cerebros dos testes
class Espiao(PoliticaInstintoMundo):
    """o instinto do mundo que, a cada decisao, guarda o `obs.social` e a conta de referencia do cheiro, refeita do estado do grupo na hora
    da decisao (o motor e posto pela fabrica). Com `barulho`, o ocioso vira emburrar (para o som `emburrado` aparecer)."""

    def __init__(self, cfg=None, barulho: bool = False) -> None:
        super().__init__(cfg or CONFIG_PADRAO)
        self.barulho = barulho
        self.motor = None
        self.decisoes: list = []

    def agir(self, obs, rng):
        a = super().agir(obs, rng)
        if self.barulho and a is AcaoPet.OCIOSO:
            a = AcaoPet.EMBURRAR
        m = self.motor
        if m is None:                                   # o motor que nao se apresenta (os testes do orgao conferem no motor)
            return a
        g = m._grupo
        ref = None
        if obs.social is not None and g.cs.ligada:
            ref = []
            for i in [j for j in g.ids_presentes() if j != m.ident]:
                o = g.motores[i]
                fontes = ref_fontes(*o.pet, g.mundo.marcas.get(i, []), g.tick, g.cs)
                ref.append((i, *ref_cheiro(*m.pet, m._passo, fontes, g.cs, SUB)))
        self.decisoes.append({"tick": g.tick, "social": obs.social, "ref": ref, "acao": a, "pet": m.pet, "passo": m._passo})
        return a


def _fabricas_espiao(barulho: bool, corpo: str = "sem", layout: str = "padrao"):
    _, fm = gs.fabricas("instinto", corpo, layout)

    def fm_espiao(p, cfg, s, **kw):
        m = fm(p, cfg, s, **kw)
        p.motor = m
        return m
    return (lambda cfg=None: Espiao(cfg, barulho)), fm_espiao


def _pets(s: int, cerebro: str, entrada_b: int = 0, dono: str = "aleatorio", corpo: str = "sem", layout: str = "padrao",
          barulho: bool = False, ids=("A", "B")) -> list[PetDoGrupo]:
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    pets = []
    for ident in ids:
        entrada = 0 if ident == "A" else entrada_b * TICKS_POR_DIA
        if cerebro == "espiao":
            fp, fm = _fabricas_espiao(barulho, corpo, layout)
        else:
            fp, fm = gs.fabricas(cerebro, corpo, layout)
        d = DonoComLugar(criar_dono(dono), "perto", sementes[ident], dono, gs.gdp.LAYOUTS[layout])
        pets.append(PetDoGrupo(ident, entrada, fp, fm, d, dono, cerebro))
    return pets


def _grupo(s: int, cerebro: str, cs: ConfigSentidos | None = CS, dias: int = DIAS, **kw) -> Grupo:
    layout = kw.get("layout", "padrao")
    return simular_grupo(gs.gdp.LAYOUTS[layout], s, _pets(s, cerebro, **kw), dias, cfg_sentidos=cs)


def _cerebro(g: Grupo, ident: str):
    return g.motores[ident].politica._pm


def _sem_sentidos(resumo: dict) -> dict:
    """o resumo do grupo sem o que so existe com a chave (o bloco `sentidos` e o rastro no mundo)"""
    r = dict(resumo)
    r.pop("sentidos", None)
    r["mundo"] = {k: v for k, v in r["mundo"].items() if k != "marcas"}
    return r


def _registro_sem_sentidos(g: Grupo) -> str:
    cab = {k: v for k, v in g.registro.cabecalho.items() if k != "sentidos"}
    return RegistroGrupo(cab, g.registro.eventos).para_jsonl()


# ================================================================== a config
def test_a_config_dos_sentidos_e_o_registro():
    """a chave do mundo; os numeros do mundo sao os da ConfigOlfato e da ConfigOuvido (uma config so), com o `ligada` delas independente"""
    assert CONFIG_SENTIDOS.ligada is False and CS.ligada is True
    assert CS.olfato == CONFIG_OLFATO and CS.ouvido == CONFIG_OUVIDO and not CS.olfato.ligada and not CS.ouvido.ligada
    assert set(PARAMETROS_SENTIDOS) == {"ligada"}
    assert CS.ouvido.raio_som_celulas == 16                         # o R_som do desenho (secao 5.4)
    assert CS.olfato.max_marcas * CONFIG_PADRAO.intervalo_decisao_ticks == CS.olfato.idade_marca
    with pytest.raises(TypeError):
        ConfigSentidos(ligada=1)
    with pytest.raises(TypeError):
        ConfigSentidos(olfato=CONFIG_OUVIDO)
    assert SONS == ("comendo", "bola", "chamado", "emburrado")


# ================================================================== G2
def test_g2_a_chave_desligada_e_o_gabarito_de_antes():
    """os 84 grupos de tests/gabaritos/sentidos_vidas_de_hoje.json, gravados antes do degrau 1b, byte a byte"""
    gravado = json.loads(gs.ARQUIVO.read_text(encoding="utf-8"))
    novo = gs.gerar()
    assert len(gravado) == 84 and set(novo) == set(gravado)
    assert [k for k in gravado if novo[k] != gravado[k]] == []


def test_g2_desligada_nada_dos_sentidos():
    g = _grupo(101, "espiao", cs=None)
    assert g.cs == CONFIG_SENTIDOS and g.mundo.marcas is None and not hasattr(g, "sons")
    assert "sentidos" not in g.registro.cabecalho and "sentidos" not in g.resumo() and "marcas" not in g.mundo.resumo()
    sociais = [d["social"] for d in _cerebro(g, "A").decisoes if d["social"] is not None]
    assert sociais and all(s.sentidos is None for s in sociais)


@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
def test_g2_ligada_com_um_pet_so_nada_e_guardado(cerebro):
    """sozinho no grupo (desenho, secao 5): nenhuma marca, nenhum som, a percepcao social None, e a vida de hoje"""
    for s in (101, 202):
        pets = _pets(s, cerebro, ids=("A",))
        off = simular_grupo(CM, s, pets, DIAS)
        on = simular_grupo(CM, s, _pets(s, cerebro, ids=("A",)), DIAS, cfg_sentidos=CS)
        assert on.mundo.marcas == {} and on.sons == []
        assert on.perceber_social("A") is None
        assert _texto(_sem_sentidos(on.resumo())) == _texto(off.resumo())
        assert _registro_sem_sentidos(on) == off.registro.para_jsonl()


@pytest.mark.parametrize("cerebro", ["instinto", "lobos", "espiao"])
@pytest.mark.parametrize("entrada_b", [0, 1])
@pytest.mark.parametrize("corpo", ["sem", "drives"])
def test_g2_ligada_com_dois_pets_os_cerebros_de_hoje_vivem_a_mesma_vida(cerebro, entrada_b, corpo):
    """os sentidos so somam registros: o mundo nao sorteia nada para eles, e nenhum cerebro de hoje os le. Com a chave ligada, o grupo e o
    de antes, fora o rastro, os sons e o cabecalho"""
    for s in (101, 202):
        off = _grupo(s, cerebro, cs=None, entrada_b=entrada_b, corpo=corpo)
        on = _grupo(s, cerebro, entrada_b=entrada_b, corpo=corpo)
        assert on.sons and on.mundo.marcas
        assert _texto(_sem_sentidos(on.resumo())) == _texto(off.resumo())
        assert _registro_sem_sentidos(on) == off.registro.para_jsonl()


def test_g2_ligada_o_cerebro_do_grupo_da_bancada():
    """o cerebro do grupo da bancada (o alvo aprendido, as entradas sociais, o modelo dos outros, a presenca da fruta) com a chave: a mesma
    vida, so com os sentidos a mais"""
    b = gs.bancada_do_grupo("completa").bancada_grupo()
    for braco, k in (("B+Ainf", 1), ("B+Aing", 1)):
        for s in (101, 202):
            eg = bv.EspecGrupo(braco, s, k)
            pets = b.pets_do_grupo(eg)
            cm = b.cfg_mundo_de(bv.mundo_de(eg.mundo))
            dias = b.dias_do_grupo(eg)
            off = simular_grupo(cm, s, pets, dias, cfg_grupo=b.cfg_grupo())
            on = simular_grupo(cm, s, b.pets_do_grupo(eg), dias, cfg_grupo=b.cfg_grupo(), cfg_sentidos=CS)
            assert on.sons
            assert _texto(_sem_sentidos(on.resumo())) == _texto(off.resumo())


# ================================================================== G-SENTIDOS: a conta do cheiro e o rastro
def test_a_conta_do_cheiro_da_comida_nao_mudou():
    """`cheiro_em` e `direcao_do_cheiro` agora passam pelo `campo_em` e pelo `direcao_do_campo`: a mesma conta, em 2000 casos"""
    rng = random.Random(101)
    raio = CM.raio_cheiro_celulas * SUB
    for _ in range(2000):
        x, y = rng.randrange(0, 1024), rng.randrange(0, 480)
        fontes = [(rng.randrange(0, 1024), rng.randrange(0, 480), rng.choice((32, 64))) for _ in range(rng.randrange(0, 6))]
        assert cheiro_em(x, y, fontes, CM) == ref_campo(x, y, fontes, raio) == campo_em(x, y, fontes, raio)
        assert direcao_do_cheiro(x, y, fontes, CM) == ref_direcao(x, y, fontes, raio, SUB) == direcao_do_campo(x, y, fontes, raio, SUB)


def test_as_fontes_do_pet_e_a_marca_que_some():
    cs = CS
    t = 10_000
    marcas = [(100, 100, t - cs.olfato.idade_marca), (110, 100, t - cs.olfato.idade_marca + 1), (120, 100, t - cs.olfato.idade_marca // 2), (130, 100, t)]
    f = fontes_do_pet(50, 60, marcas, t, cs.olfato)
    assert f == [(50, 60, cs.olfato.cheiro_pet), (120, 100, cs.olfato.cheiro_marca * (cs.olfato.idade_marca - cs.olfato.idade_marca // 2) // cs.olfato.idade_marca), (130, 100, cs.olfato.cheiro_marca)]
    # a marca de idade T - 1 vale A_marca x 1 // T = 0 e nao conta; a de idade T some
    assert f == ref_fontes(50, 60, marcas, t, cs)
    with pytest.raises(ValueError):
        fontes_do_pet(0, 0, [(0, 0, t + 1)], t, cs.olfato)


def test_o_rastro_no_mundo_uma_marca_por_decisao_ate_o_maximo():
    m = Mundo(CONFIG_MUNDO_LIGADA, 101)
    with pytest.raises(ValueError):
        m.deixar_marca("A", 0, 0, 0, CS.olfato)
    m.ligar_marcas()
    cs = replace(CS.olfato, max_marcas=3, idade_marca=60)
    for k in range(6):
        m.deixar_marca("A", k, 0, 15 * k, cs)
    assert m.marcas_de("A") == [(3, 0, 45), (4, 0, 60), (5, 0, 75)]
    m.deixar_marca("A", 9, 9, 200, cs)                      # as de idade >= T saem antes
    assert m.marcas_de("A") == [(9, 9, 200)]
    with pytest.raises(ValueError):
        m.deixar_marca("A", 0, 0, 199, cs)                  # fora de ordem
    assert m.resumo()["marcas"] == {"A": [[9, 9, 200]]}


@pytest.mark.parametrize("entrada_b", [0, 1])
def test_o_rastro_e_a_posicao_de_cada_decisao_com_os_dois_presentes(entrada_b):
    """o rastro de cada pet sao as ultimas `max_marcas` decisoes, no ponto `antes` de cada uma, so depois de os dois estarem presentes, sem
    as de idade T"""
    for s in (101, 202):
        g = _grupo(s, "instinto", entrada_b=entrada_b)
        inicio = entrada_b * TICKS_POR_DIA
        for i, m in g.motores.items():
            todas = [(d["antes"][0], d["antes"][1], d["tick"]) for d in m.decisoes_mundo if d["tick"] >= inicio]
            ultima = todas[-1][2]
            esperado = [e for e in todas if ultima - e[2] < CS.olfato.idade_marca][-CS.olfato.max_marcas:]
            guardado = g.mundo.marcas_de(i)
            assert guardado == esperado and len(guardado) == CS.olfato.max_marcas
            assert all(t >= inicio for *_, t in guardado)


@pytest.mark.parametrize("barulho", [False, True])
@pytest.mark.parametrize("layout", ["padrao", "afastado"])
def test_o_cheiro_de_cada_outro_na_hora_de_cada_decisao(barulho, layout):
    """em toda decisao com o outro presente, o `obs.social.sentidos.cheiro` e a conta refeita do estado do grupo naquele momento (a posicao
    do outro, o rastro dele no mundo, a posicao e o passo do proprio pet), com a direcao e as duas narinas"""
    vistos = com_cheiro = 0
    for s in (101, 202, 303):
        g = _grupo(s, "espiao", layout=layout, barulho=barulho)
        for i in g.motores:
            for d in _cerebro(g, i).decisoes:
                if d["social"] is None:
                    continue
                sen = d["social"].sentidos
                assert isinstance(sen, PercepcaoSentidos)
                assert tuple(d["ref"]) == sen.cheiro
                assert sen.passo == d["passo"]
                vistos += 1
                com_cheiro += any(c[1] > 0 for c in sen.cheiro)
    assert vistos > 500 and com_cheiro > 50


def test_a_narina_do_lado_do_outro_sente_mais():
    """com o outro parado a esquerda (a norte de quem olha para leste), a narina esquerda sente mais; a direcao pronta aponta para ele"""
    raio = CS.olfato.raio_celulas * SUB
    fontes = [(500, 200 - 5 * SUB, 1024)]                  # forte, sem empate de arredondamento na direcao
    centro, direcao = direcao_do_campo(500, 200, fontes, raio, SUB)
    esq, dir_ = pontos_laterais(500, 200, 0, CS.olfato.afastamento_narinas)
    assert direcao == 3                                     # N
    assert campo_em(*esq, fontes, raio) > campo_em(*dir_, fontes, raio)
    # olhando para oeste (passo 8), o outro fica a direita
    esq, dir_ = pontos_laterais(500, 200, 8, CS.olfato.afastamento_narinas)
    assert campo_em(*esq, fontes, raio) < campo_em(*dir_, fontes, raio)


# ================================================================== G-SENTIDOS: o som
def test_um_som_por_evento_na_posicao_do_pet():
    """comer (comer e o achou e comeu), a bola, chamar e emburrar: um som por evento, no tick e na posicao do pet depois da acao; nada antes
    de os dois estarem presentes"""
    contagem = {s: 0 for s in SONS}
    for entrada_b in (0, 1):
        for s in (101, 202, 303):
            g = _grupo(s, "espiao", barulho=True, entrada_b=entrada_b)
            inicio = entrada_b * TICKS_POR_DIA
            for i, m in g.motores.items():
                esperado = []
                for d in m.decisoes_mundo:
                    if d["tick"] < inicio:
                        continue
                    if d["acao"] == "chamar_atencao":
                        esperado.append((d["tick"], "chamado", d["x"], d["y"]))
                    elif d["acao"] == "emburrar":
                        esperado.append((d["tick"], "emburrado", d["x"], d["y"]))
                    if d["comeu"] is not None:
                        esperado.append((d["tick"], "comendo", d["x"], d["y"]))
                    if d["brincou_com_bola"]:
                        esperado.append((d["tick"], "bola", d["x"], d["y"]))
                emitidos = [(e["tick"], e["som"], e["x"], e["y"]) for e in g.sons if e["emissor"] == i]
                assert sorted(emitidos) == sorted(esperado)
                for e in emitidos:
                    contagem[e[1]] += 1
    assert all(n > 0 for n in contagem.values()), contagem


@pytest.mark.parametrize("layout", ["padrao", "afastado"])
def test_o_som_ouvido_a_conta_e_o_alcance(layout):
    """quem ouve: todo outro presente a d < R_som, e so ele; a direcao, a distancia e as intensidades refeitas de onde cada um estava"""
    ouvidos = fora = 0
    for s in (101, 202, 303):
        g = _grupo(s, "espiao", barulho=True, layout=layout)
        for e in g.sons:
            assert set(e["outros"]) == {i for i in g.motores if i != e["emissor"]}
            for i, (lx, ly, passo) in e["outros"].items():
                r = ref_som(lx, ly, passo, e["x"], e["y"], CS, SUB)
                assert (r is not None) == (i in e["ouvintes"])
                assert som_ouvido(lx, ly, passo, e["x"], e["y"], CS.ouvido, SUB) == r
                ouvidos += r is not None
                fora += r is None
    assert ouvidos > 100 and fora > 10


@pytest.mark.parametrize("entrada_b", [0, 1])
def test_a_caixa_dos_sons_chega_inteira_a_decisao_seguinte(entrada_b):
    """os sons de cada decisao sao os ouvidos desde a decisao anterior, na ordem; somados a caixa do fim, sao todos os ouvidos; a idade e o
    tick da decisao menos o do som; o proprio pet nunca se ouve"""
    for s in (101, 202):
        g = _grupo(s, "espiao", barulho=True, entrada_b=entrada_b)
        for i, m in g.motores.items():
            recebidos = []
            for d in _cerebro(g, i).decisoes:
                if d["social"] is None:
                    continue
                for son in d["social"].sentidos.sons:
                    assert son[0] != i and son[-1] >= 0
                    recebidos.append((son[0], son[1], d["tick"] - son[-1], son[2:7]))
            recebidos += [(son[0], son[1], son[7], son[2:7]) for son in m._sons_ouvidos]
            esperado = []
            for e in g.sons:
                if i in e["ouvintes"]:
                    lx, ly, passo = e["outros"][i]
                    esperado.append((e["emissor"], e["som"], e["tick"], ref_som(lx, ly, passo, e["x"], e["y"], CS, SUB)))
            assert recebidos == esperado and esperado


def test_o_ouvido_do_lado_do_som_ouve_mais():
    r = som_ouvido(500, 200, 0, 500, 200 - 4 * SUB, CS.ouvido, SUB)       # o som ao norte de quem olha para leste: a esquerda
    direcao, d, centro, esq, dir_ = r
    assert direcao == 3 and d == 4 * SUB and esq > dir_ and centro == CS.ouvido.som * (16 * SUB - d) // (16 * SUB)
    assert som_ouvido(0, 0, 0, 16 * SUB, 0, CS.ouvido, SUB) is None          # d = R_som: fora
    assert som_ouvido(0, 0, 0, 16 * SUB - 1, 0, CS.ouvido, SUB) is not None


def test_o_som_desconhecido_falha_alto():
    g = _grupo(101, "instinto", dias=1)
    with pytest.raises(ValueError):
        g.emitir_som("A", "latido")


# ================================================================== a geometria das duas posicoes de amostra
def test_as_direcoes_e_os_pontos_laterais():
    for j, (cx, cy) in enumerate(DIR16):
        assert direcao_em_16(cx, cy) == j
        assert direcao_em_16(3 * cx, 3 * cy) == j
    assert direcao_em_16(0, 0) is None and direcao_em_8(0, 0) == 0
    rng = random.Random(202)
    for _ in range(3000):
        dx, dy = rng.randrange(-500, 501), rng.randrange(-500, 501)
        assert direcao_em_8(dx, dy) == ref_direcao_8(dx, dy)
        passo, af = rng.randrange(16), rng.randrange(0, 40)
        x, y = rng.randrange(1024), rng.randrange(480)
        assert pontos_laterais(x, y, passo, af) == ref_laterais(x, y, passo, af)
    assert pontos_laterais(10, 20, 3, 0) == ((10, 20), (10, 20))
    assert pontos_laterais(100, 100, 0, 8) == ((100, 92), (100, 108))     # leste: a esquerda e o norte (y menor)


def test_o_passo_e_a_direcao_do_ultimo_deslocamento():
    """antes do primeiro passo, `passo_inicial`; depois, a direcao (DIR16) do ultimo deslocamento de uma decisao, e nao muda parado"""
    for s in (101, 202):
        g = _grupo(s, "espiao")
        for i, m in g.motores.items():
            passo = PASSO_INICIAL
            decs = iter(m.decisoes_mundo)
            for d in _cerebro(g, i).decisoes:
                assert d["passo"] == passo
                dm = next(decs)
                if (dm["x"], dm["y"]) != tuple(dm["antes"]):
                    passo = direcao_em_16(dm["x"] - dm["antes"][0], dm["y"] - dm["antes"][1])
            assert m._passo == passo


# ================================================================== G-RECEPTOR-SOCIAL
def test_a_percepcao_dos_sentidos_so_tem_o_fisico():
    assert [f.name for f in fields(PercepcaoSocial)] == ["outros", "onde_comeu", "toque", "sentidos"]
    assert [f.name for f in fields(PercepcaoSentidos)] == ["passo", "cheiro", "sons"]
    g = _grupo(101, "espiao", barulho=True)
    vistos = 0
    for d in _cerebro(g, "A").decisoes:
        if d["social"] is None:
            continue
        sen = d["social"].sentidos
        assert type(sen.passo) is int
        for item in sen.cheiro + sen.sons:
            assert all(type(v) in (int, str) for v in item), item
            vistos += 1
    assert vistos > 0


def test_o_estado_interno_do_outro_nao_muda_o_que_se_sente():
    """mudar a fome, o humor e o cerebro do B, sem mudar onde ele esta, o rastro dele e o que ele fez soar, nao muda o que o A sente"""
    g = _grupo(202, "lobos", dias=2)
    antes = g.perceber_social("A")
    b = g.motores["B"]
    b._estado = replace(b._estado, fome=0.01, humor=0.99, energia=0.02)
    pol = b.politica._pm
    pol._pesos = {k: v for k, v in pol._pesos.items()} if hasattr(pol, "_pesos") else None
    b._sons_ouvidos.append(("A", "chamado", 1, 1, 1, 1, 1, g.tick))     # o que o B ouviu e do B
    depois = g.perceber_social("A")
    assert depois.sentidos == antes.sentidos
    x, y = b.pet
    b.pet = (x + 3 * SUB, y)                                            # onde ele esta muda o cheiro
    assert g.perceber_social("A").sentidos.cheiro != antes.sentidos.cheiro


# ================================================================== G1-GRUPO com os sentidos
@pytest.mark.parametrize("cerebro", ["instinto", "lobos"])
@pytest.mark.parametrize("entrada_b", [0, 1])
@pytest.mark.parametrize("corpo", ["sem", "drives"])
@pytest.mark.parametrize("layout", ["padrao", "afastado"])
def test_g1_o_replay_refaz_os_sentidos(cerebro, entrada_b, corpo, layout):
    s = 303
    pets = _pets(s, cerebro, entrada_b=entrada_b, corpo=corpo, layout=layout)
    g = simular_grupo(gs.gdp.LAYOUTS[layout], s, pets, DIAS, cfg_sentidos=CS)
    assert g.registro.cabecalho["sentidos"] == asdict(CS)
    texto = g.registro.para_jsonl()
    fabricas = {p.ident: (p.politica_fabrica, p.fabrica_motor) for p in _pets(s, cerebro, entrada_b=entrada_b, corpo=corpo, layout=layout)}
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(texto), fabricas, gs.gdp.LAYOUTS[layout], cfg_sentidos=CS)
    assert _texto(r.resumo()) == _texto(g.resumo())
    assert r.resumo()["sentidos"]["sons"] and r.mundo.marcas
    with pytest.raises(ValueError):
        reproduzir_grupo(RegistroGrupo.de_jsonl(texto), fabricas, gs.gdp.LAYOUTS[layout])                       # sem a chave
    with pytest.raises(ValueError):
        reproduzir_grupo(RegistroGrupo.de_jsonl(texto), fabricas, gs.gdp.LAYOUTS[layout], cfg_sentidos=replace(CS, ouvido=replace(CS.ouvido, raio_som_celulas=8)))


# ================================================================== o lado do mundo do orgao do corpo (etapa 8b: `_intensidades_do_orgao`)
OLFATO_ON = replace(CONFIG_OLFATO, ligada=True, comida=True, outro_pet=True)
OUVIDO_ON = replace(CONFIG_OUVIDO, ligada=True)


class MotorQueAnota(com_corpo(MotorMundo)):
    """o MotorMundo com o corpo e os orgaos, de verdade; so anota cada entrega do lado do mundo (o tick do mundo, a posicao, o passo, o
    que entregou)"""

    def _intensidades_do_orgao(self):
        out = super()._intensidades_do_orgao()
        self.__dict__.setdefault("entregas", []).append((self._tm(self._estado.tick), self.pet, self._passo, dict(out)))
        return out


def _fm_orgao(co=OLFATO_ON, cv=OUVIDO_ON, layout="padrao"):
    cm = gs.gdp.LAYOUTS[layout]
    return lambda p, cfg, s, **kw: MotorQueAnota(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm,  # noqa: E731
                                                 cfg_corpo=CONFIG_CORPO_DRIVES, cfg_olfato=co, cfg_ouvido=cv, **kw)


def _pets_orgao(s, entrada_b=0, dono="aleatorio", co=OLFATO_ON, cv=OUVIDO_ON, ids=("A", "B")):
    sementes = sementes_do_grupo(s, CONFIG_GRUPO_LIGADA.ids)
    out = []
    for ident in ids:
        fp = lambda cfg=None: Espiao(cfg, True)  # noqa: E731
        fm0 = _fm_orgao(co, cv)

        def fm(p, cfg, s_, fm0=fm0, **kw):
            m = fm0(p, cfg, s_, **kw)
            p.motor = m
            return m
        d = DonoComLugar(criar_dono(dono), "perto", sementes[ident], dono, CM)
        out.append(PetDoGrupo(ident, 0 if ident == "A" else entrada_b * TICKS_POR_DIA, fp, fm, d, dono, "espiao"))
    return out


def test_o_orgao_le_o_mundo_nos_pontos_das_narinas_um_pet():
    """sozinho no mundo: o olfato da comida e a conta do cheiro da comida no ponto de cada narina (pela direcao do ultimo passo); o do outro
    e o ouvido, 0"""
    g = simular_grupo(CM, 101, _pets_orgao(101, ids=("A",)), 2, cfg_sentidos=CS)
    m = g.motores["A"]
    assert len(m.entregas) > 2 * TICKS_POR_DIA                       # antes de cada tick e de cada percepcao
    raio = CM.raio_cheiro_celulas * SUB
    com_cheiro = 0
    for agora, (x, y), passo, out in m.entregas:
        fontes = m.mundo.fontes_de_cheiro(agora) if agora == g.tick else None
        assert set(out) == {o.receptor for o in m.corpo.orgaos}
        assert out["olfato_outro_esq"] == out["olfato_outro_dir"] == 0
        assert all(v == 0 for k, v in out.items() if k.startswith("ouvido_"))
        com_cheiro += out["olfato_comida_esq"] > 0
        if fontes is not None:
            esq, dir_ = ref_laterais(x, y, passo, OLFATO_ON.afastamento_narinas)
            assert out["olfato_comida_esq"] == ref_campo(*esq, fontes, raio)
            assert out["olfato_comida_dir"] == ref_campo(*dir_, fontes, raio)
    assert com_cheiro > 100


def test_o_orgao_le_o_mundo_na_hora_de_cada_entrega():
    """a conta refeita na hora: o olfato da comida e do outro, decisao a decisao (o Espiao confere o estado do grupo no momento)"""

    class MotorConfere(MotorQueAnota):
        def _intensidades_do_orgao(self):
            out = super()._intensidades_do_orgao()
            g, agora = self._grupo, self._tm(self._estado.tick)
            x, y = self.pet
            raio_c, raio_o = CM.raio_cheiro_celulas * SUB, OLFATO_ON.raio_celulas * SUB
            pts = ref_laterais(x, y, self._passo, OLFATO_ON.afastamento_narinas)
            for lado, pt in zip(("esq", "dir"), pts):
                assert out[f"olfato_comida_{lado}"] == ref_campo(*pt, self.mundo.fontes_de_cheiro(agora), raio_c)
                v = 0
                for i in [j for j in g.ids_presentes() if j != self.ident]:
                    o = g.motores[i]
                    v += ref_campo(*pt, ref_fontes(*o.pet, g.mundo.marcas.get(i, []), agora, CS), raio_o)
                assert out[f"olfato_outro_{lado}"] == v
            self.__dict__.setdefault("conferidas", 0)
            self.conferidas += 1
            return out

    pets = []
    for p in _pets_orgao(202):
        fm = lambda pol, cfg, s, **kw: MotorConfere(pol, cfg, s, obediencia_desligada=True, cfg_mundo=CM,  # noqa: E731
                                                    cfg_corpo=CONFIG_CORPO_DRIVES, cfg_olfato=OLFATO_ON, cfg_ouvido=OUVIDO_ON, **kw)
        pets.append(replace(p, fabrica_motor=fm))
    g = simular_grupo(CM, 202, pets, 2, cfg_sentidos=CS)
    assert all(m.conferidas > 2 * TICKS_POR_DIA for m in g.motores.values())
    assert any(e[3]["olfato_outro_esq"] > 0 for m in g.motores.values() for e in m.entregas)


@pytest.mark.parametrize("entrada_b", [0, 1])
def test_cada_som_entra_no_ouvido_em_um_tick_so(entrada_b):
    """o estimulo do ouvido de cada tick e a soma dos sons daquele tipo que entram nele; somando um valor por tick, cada som ouvido conta
    exatamente uma vez, com a intensidade de cada ouvido de onde o pet estava quando o som soou"""
    for s in (101, 202):
        g = simular_grupo(CM, s, _pets_orgao(s, entrada_b), DIAS, cfg_sentidos=CS)
        assert g.sons
        for i, m in g.motores.items():
            por_tick = {}
            for agora, _, _, out in m.entregas:
                por_tick[agora] = out                                 # o ultimo do tick (a percepcao e o passo dao o mesmo)
            for som in SONS:
                for lado, k in (("esq", 3), ("dir", 4)):
                    total = sum(out[f"ouvido_{som}_{lado}"] for out in por_tick.values())
                    esperado = sum(ref_som(*e["outros"][i], e["x"], e["y"], CS, SUB)[k]
                                   for e in g.sons if i in e["ouvintes"] and e["som"] == som)
                    pendente = sum(x[k] for x in m._sons_orgao if x[1] == som and x[0] > max(por_tick))
                    assert total + pendente == esperado, (i, som, lado)


def test_o_orgao_no_grupo_falha_alto_sem_o_mundo_dos_sentidos():
    with pytest.raises(ValueError, match="ConfigSentidos"):
        simular_grupo(CM, 101, _pets_orgao(101), 1)
    with pytest.raises(ValueError, match="ConfigSentidos"):
        simular_grupo(CM, 101, _pets_orgao(101, co=replace(OLFATO_ON, outro_pet=False)), 1)
    with pytest.raises(ValueError, match="numeros do mundo"):
        simular_grupo(CM, 101, _pets_orgao(101, co=replace(OLFATO_ON, raio_celulas=12)), 1, cfg_sentidos=CS)
    with pytest.raises(ValueError, match="numeros do mundo"):
        simular_grupo(CM, 101, _pets_orgao(101, cv=replace(OUVIDO_ON, som=8)), 1, cfg_sentidos=CS)
    # so o olfato da comida: o grupo sem os sentidos basta
    simular_grupo(CM, 101, _pets_orgao(101, co=replace(OLFATO_ON, outro_pet=False), cv=CONFIG_OUVIDO), 1)


def test_g1_o_replay_refaz_o_orgao_no_grupo():
    s = 303
    g = simular_grupo(CM, s, _pets_orgao(s, 1), DIAS, cfg_sentidos=CS)
    fabricas = {p.ident: (p.politica_fabrica, p.fabrica_motor) for p in _pets_orgao(s, 1)}
    r = reproduzir_grupo(RegistroGrupo.de_jsonl(g.registro.para_jsonl()), fabricas, CM, cfg_sentidos=CS)
    assert _texto(r.resumo()) == _texto(g.resumo())
    assert {i: m.corpo.para_dict() for i, m in r.motores.items()} == {i: m.corpo.para_dict() for i, m in g.motores.items()}
