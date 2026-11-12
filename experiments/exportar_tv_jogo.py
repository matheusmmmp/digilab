"""O gabarito da TV no jogo para a web (GOSTO_VISUAL, as decisoes A, B e D da captura ligada ao cerebro; "Sim a tudo", Matheus, 2026-11-12;
docs/registro/2026-11.md, D-GV-TVJOGO): a paridade da TV desligada, do ir ate a TV e da TV no grupo com o motor TS (`web/app/motor/tv.ts`,
`mundo.ts`, `motor_corpo_mundo.ts`, `grupo.ts` e `digibrain/`). O TS confere o arquivo em `web/app/test/tv_jogo_paridade.test.ts`, bit a
bit no Node.

O que vai no arquivo (`web/app/test/gabaritos/tv_jogo.json.gz`, so; nada dos gabaritos de hoje e regravado):
  - as vidas de um pet so: o laboratorio com o olhar (a vida do gosto visual, `exportar_gosto_visual.viver`, a fonte "evento" com o agrado
    no corpo), com a ConfigTVJogo ligada (a TV desligada e o ir ate a TV) e o DigiBrain com o `ir_ate_tv`; o dono e o do gosto visual, e a TV
    fica desligada das 20 h as 23 h de cada dia (`desligar_tela`). Sementes dos testes, 3 dias. O TS rejoga o log e confere, decisao a
    decisao, a acao, o motivo, a assinatura de cada modulo e os estimulos do corpo; no fim, o estado interno do cerebro, o corpo, o mundo
    fisico e o registro da TV;
  - as vidas do grupo de dois pets com a TV do mundo comum (Grupo(cfg_tv=, cfg_tv_jogo=)): cada pet e o laco do corpo com o mundo e o
    mesmo laboratorio com o olhar e o ir ate a TV; o mesmo roteiro da TV, a racao no comedouro para os dois. A semente do segundo pet e a do
    jogo (o derivar_semente("segundo-pet", s) cortado aos 32 bits, D-CO4b-2), para o TS montar o laco dele com uma semente do jogo. O TS
    rejoga o registro do grupo e confere, de cada pet, a acao e o motivo de cada decisao, o estado interno do cerebro no fim, o mundo fisico
    e, do mundo comum, o registro da TV.
Nao sao vidas de pesquisa (sementes dos testes; nenhuma faixa reservada). Nenhum numero nasce aqui.

    python experiments/exportar_tv_jogo.py            # grava web/app/test/gabaritos/tv_jogo.json.gz
"""
from __future__ import annotations

import gzip
import hashlib
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as E  # noqa: E402
import exportar_gosto_visual as X  # noqa: E402

from digilab.config import CANAIS_TELA, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, CONFIG_TVJOGO_LIGADA  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.events import AcaoUsuario, ler_sentido_tela  # noqa: E402
from digilab.grupo import Grupo, ROTULO_SEGUNDO_PET  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, centro_da_celula  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.tv import ResumoTela  # noqa: E402

ARQUIVO = E.PASTA / "tv_jogo.json.gz"
FONTE = "evento"
SEMENTES = (101, 202, 303)                        # as dos testes
SEMENTES_GRUPO = (101, 202)
DIAS = 3
DIAS_GRUPO = 2
FLUXO_DONO = "gabarito-tv-jogo"                   # a rng do exportador: so escolhe o que vai no log (nenhum fluxo do motor)
HORA = 60
DESLIGADA = (20, 21, 22)                          # as horas do dia com a TV desligada (o desligar_tela as 20 h; religa as 23 h)
CTV = X.config_tv(FONTE)


def cerebro(semente: int) -> DigiBrain:
    return DigiBrain(CONFIG_PADRAO, X.config_vida(), X.orq.CM, semente=semente, cfg_olhar=X.config_olhar(FONTE), ir_ate_tv=True)


def laco(politica, semente: int, **kw):
    return com_corpo(MotorMundo)(politica, CONFIG_PADRAO, semente, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=X.orq.CM,
                                 cfg_corpo=X._cc(), cfg_tela=X.TELA, cfg_tv=CTV, cfg_tv_jogo=CONFIG_TVJOGO_LIGADA, **kw)


def roteiro_tv(h: int, resumo: ResumoTela, rng: random.Random, tick: int, sentir, desligar) -> ResumoTela:
    """a TV da hora h: desligada das 20 h as 23 h (o desligar_tela uma vez, as 20 h); nas outras, 30 amostras (o evento so na mudanca)"""
    hora = h % 24
    if hora == DESLIGADA[0]:
        desligar()
        return ResumoTela("tv")                   # a TV religa com um resumo novo (o primeiro evento sempre sai)
    if hora in DESLIGADA:
        return resumo
    for _ in range(30):
        ev = resumo.amostra(tick, tuple(rng.random() for _ in CANAIS_TELA))
        if ev is not None:
            sentir(*ler_sentido_tela(ev))
    return resumo


def viver(semente: int, gravar: bool = True):
    c = cerebro(semente)
    g = E.Gravador(c) if gravar else None
    estimulos: list[list] = []
    gancho = c.consequencia_corpo

    def consequencia_corpo(acao, ocorrido, obs):
        estimulos.append(E.paraj(ocorrido["estimulos"]))
        return gancho(acao, ocorrido, obs)
    c.consequencia_corpo = consequencia_corpo
    try:
        m = laco(c, semente)
        rng = random.Random(derivar_semente(FLUXO_DONO, semente))
        x, y = centro_da_celula(X.orq.CM.layout.comedouro, X.orq.CM)
        r = ResumoTela("tv")
        for h in range(DIAS * 24):
            r = roteiro_tv(h, r, rng, m.estado()["tick"], m.sentido_tela, lambda: m.desligar_tela("tv"))
            m.avancar(HORA)
            if h % 3 == 0:
                m.deixar_comida("racao", x, y)
            if h % 5 == 2 and not m.estado()["dormindo"]:
                m.observar(AcaoUsuario.ACARICIAR)
    finally:
        if g is not None:
            g.soltar()
    return m, c, g, estimulos


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _vida(semente: int) -> dict:
    m, c, g, estimulos = viver(semente)
    ms = c.motivos
    if len(estimulos) != len(ms):
        raise RuntimeError("os estimulos e as decisoes divergem")
    acoes = [x["acao"] for x in ms]
    if "ir_tv" not in acoes or not any(x["olhar"]["olha"] is not None for x in ms):
        raise RuntimeError(f"a vida {semente} nunca foi ate a TV ou nunca a olhou")
    return {"semente": semente, "dias": DIAS, "ir_tv": acoes.count("ir_tv"), "olhares": sum(1 for x in ms if x["olhar"]["olha"] is not None),
            "decisoes": [{"k": k, "acao": ms[k]["acao"], "assinatura": g.assinaturas[k], "motivo": E.paraj(ms[k]),
                          "estimulos": estimulos[k]} for k in range(len(ms))],
            "log": [ev.para_dict() for ev in m.log], "log_sha256": _sha(m.log.para_jsonl()),
            "estado": _sha(E._texto(E.paraj(c.estado_interno()))), "assinatura_final": g.assinar(), "corpo": E.paraj(m.corpo.para_dict()),
            "fisico": _sha(E._texto(E.paraj(m.resumo_mundo_fisico()))), "decisoes_mundo": E.paraj(m.decisoes_mundo),
            "tv": E.paraj(m.mundo.tv.resumo())}


def semente_do_segundo_jogo(semente: int) -> int:
    """a do grupo do jogo (motor/grupo_jogo.ts, sementeDoSegundoJogo; D-CO4b-2)"""
    return derivar_semente(ROTULO_SEGUNDO_PET, semente) & 0xFFFFFFFF


def viver_grupo(semente: int) -> Grupo:
    g = Grupo(X.orq.CM, semente, CONFIG_GRUPO_LIGADA, CONFIG_PADRAO, cfg_tv=CTV, cfg_tv_jogo=CONFIG_TVJOGO_LIGADA)
    g.sementes[CONFIG_GRUPO_LIGADA.ids[1]] = semente_do_segundo_jogo(semente)
    for i in g.cg.ids:
        s = g.sementes[i]
        g.entrar(i, cerebro(s), lambda p, cfg, sem, **kw: laco(p, sem, **kw), "modular", "gabarito")
    rng = random.Random(derivar_semente(FLUXO_DONO, "grupo", semente))
    x, y = centro_da_celula(X.orq.CM.layout.comedouro, X.orq.CM)
    r = ResumoTela("tv")
    for h in range(DIAS_GRUPO * 24):
        r = roteiro_tv(h, r, rng, g.tick, g.sentido_tela, lambda: g.desligar_tela("tv"))
        g.avancar(HORA)
        if h % 3 == 0:
            for i in g.cg.ids:
                g.deixar_comida(i, "racao", x, y)
    return g


def _vida_grupo(semente: int) -> dict:
    g = viver_grupo(semente)
    pets = {}
    for i, m in g.motores.items():
        ms = m.politica.motivos
        pets[i] = {"semente": g.sementes[i], "acoes": [x["acao"] for x in ms], "motivos_sha256": [_sha(E._texto(E.paraj(x))) for x in ms],
                   "estado": _sha(E._texto(E.paraj(m.politica.estado_interno()))), "corpo": E.paraj(m.corpo.para_dict()),
                   "pet": list(m.pet), "decisoes_mundo": E.paraj(m.decisoes_mundo)}
        if "ir_tv" not in pets[i]["acoes"] or not any(x["olhar"]["olha"] is not None for x in ms):
            raise RuntimeError(f"o pet {i} do grupo {semente} nunca foi ate a TV ou nunca a olhou")
    return {"semente": semente, "dias": DIAS_GRUPO, "registro": [e.para_dict() for e in g.registro.eventos],
            "cabecalho": E.paraj(g.registro.cabecalho), "pets": pets, "tv": E.paraj(g.mundo.tv.resumo()),
            "ordens": E.paraj(g.ordens), "contatos": len(g.contatos)}


def gerar() -> dict:
    return {"versao": 1, "config_tv_jogo": {"desligar": True, "ir_ate_tv": True},
            "vidas": [_vida(s) for s in SEMENTES], "grupos": [_vida_grupo(s) for s in SEMENTES_GRUPO]}


def texto() -> bytes:
    return E._texto(gerar()).encode("utf-8")


if __name__ == "__main__":
    ARQUIVO.write_bytes(gzip.compress(texto(), mtime=0))
    print(f"gravado {ARQUIVO} ({ARQUIVO.stat().st_size} bytes)")
