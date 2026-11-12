"""O gabarito do gosto visual para a web (GOSTO_VISUAL, P1f; docs/ESPEC_GOSTO_VISUAL_P1.md, secoes 1.2, 8 e 9): a paridade do orgao da tela
(P1b), da TV (P1c) e do olhar no DigiBrain modular (P1d) com o motor TS (`web/app/motor/tv.ts`, `corpo.ts`, `motor_corpo_mundo.ts` e
`digibrain/`). O TS confere o arquivo em `web/app/test/gosto_visual_paridade.test.ts`, bit a bit no Node.

O que vai no arquivo (`web/app/test/gabaritos/gosto_visual.json.gz`, so; nada dos gabaritos de hoje e regravado, e o
`digibrain_modular_constantes.json` fica como esta, D-GV-P1f-2):
  - as constantes: os canais, a `ConfigTela`, a `ConfigTV`, a `ConfigOlhar` (as duas `agrado_no_corpo`), a `ConfigDigibrain` da vida (a do
    laboratorio, o REL da C4, com a subchave `olhar`);
  - os genomas da visao (rng propria `visao-ovo`) das sementes dos testes e o vazio;
  - a grade da TV do jogo (rng propria `tv-programas`): os perfis e o que a TV passa num punhado de ticks, com uma troca de canal;
  - o `ResumoTela` (GV-15): amostras sinteticas (floats da rng do exportador) e os eventos que saem;
  - o grafo do corpo com a tela: os quimicos, os emissores e os orgaos;
  - as vidas: o laboratorio com o olhar, no mundo do produto (o `orq.CM`) e o corpo do v11, com a TV nas duas fontes:
      "grade"   a TV do jogo, com o `trocar_canal` do dono, o agrado so no sinal (a `agrado_no_corpo` desligada);
      "evento"  o modo livre gravado: o `sentido_tela` que sai do `ResumoTela` sobre amostras sinteticas (o mesmo caminho do P0 na web), com
                o agrado no corpo (a GV-16 inteira);
    nas sementes dos testes, 3 dias, com o dono do exportador (sem rng nova no motor: a racao no comedouro, o carinho e um tapa, e as
    trocas de canal ou as amostras da tela de uma rng propria do exportador, `gabarito-gosto-visual`, que so escolhe o que vai no log).
    O TS rejoga o log e confere, decisao a decisao, a acao, o motivo, a assinatura de cada modulo e os estimulos do corpo; no fim, o estado
    interno do cerebro, o corpo, as novidades da tela e o registro da TV.
Nao sao vidas de pesquisa (sementes dos testes; nenhuma faixa reservada). Nenhum numero nasce aqui: todos sao os PROPOSTOS do `config.py`.

    python experiments/exportar_gosto_visual.py            # grava web/app/test/gabaritos/gosto_visual.json.gz
"""
from __future__ import annotations

import gzip
import hashlib
import random
import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_digibrain_modular as E  # noqa: E402
import run_v2_digibrain_prototipo as orq  # noqa: E402

from digilab.config import (CANAIS_TELA, CONFIG_OLHAR, CONFIG_PADRAO, ConfigOlhar, ConfigTela, ConfigTV)  # noqa: E402
from digilab.corpo import grafo_do_corpo, taxas_de  # noqa: E402
from digilab.digibrain.adapt import DigiBrain  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.genoma_visao import genoma_visao, genoma_visao_vazio  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import MotorMundo, centro_da_celula  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402
from digilab.tv import TV, ResumoTela  # noqa: E402

ARQUIVO = E.PASTA / "gosto_visual.json.gz"
TELA = ConfigTela(ligada=True)
FONTES = ("grade", "evento")                      # a TV do jogo (o agrado so no sinal) e o modo livre gravado (o agrado tambem no corpo)
SEMENTES = (101, 202, 303)                        # as dos testes
DIAS = 3
FLUXO_DONO = "gabarito-gosto-visual"              # a rng do exportador: so escolhe o que vai no log (nenhum fluxo do motor)
HORA = 60


def config_olhar(fonte: str) -> ConfigOlhar:
    return replace(CONFIG_OLHAR, agrado_no_corpo=(fonte == "evento"))


def config_vida():
    """a ConfigDigibrain da vida: a do laboratorio (o REL da C4) com a subchave `olhar` e nada mais"""
    return replace(E.config_laboratorio(), olhar=True)


def config_tv(fonte: str) -> ConfigTV:
    return ConfigTV(ligada=True, fonte=fonte)


def _cc():
    """o corpo da vida: o do orq (o do v11), o mesmo do gabarito do modular"""
    b = orq.bancada(DIAS, orq.ORCAMENTO_POR_DIA)
    return b.cfg_corpo_de(orq.bv.EspecVida("atencioso", orq.gl.BRACO_V11, 101))


def viver(fonte: str, semente: int, gravar: bool = True):
    """a vida: (o motor, o cerebro, o gravador, os estimulos de cada decisao, o resumo da tela ou None)"""
    cerebro = DigiBrain(CONFIG_PADRAO, config_vida(), orq.CM, semente=semente, cfg_olhar=config_olhar(fonte))
    g = E.Gravador(cerebro) if gravar else None
    estimulos: list[list] = []
    gancho = cerebro.consequencia_corpo

    def consequencia_corpo(acao, ocorrido, obs):
        estimulos.append(E.paraj(ocorrido["estimulos"]))
        return gancho(acao, ocorrido, obs)
    cerebro.consequencia_corpo = consequencia_corpo
    try:
        m = com_corpo(MotorMundo)(cerebro, CONFIG_PADRAO, semente, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=orq.CM,
                                  cfg_corpo=_cc(), cfg_tela=TELA, cfg_tv=config_tv(fonte))
        rng = random.Random(derivar_semente(FLUXO_DONO, fonte, semente))
        x, y = centro_da_celula(orq.CM.layout.comedouro, orq.CM)
        resumo = ResumoTela("tv") if fonte == "evento" else None
        for h in range(DIAS * 24):
            if resumo is not None:                # 30 amostras por hora: 3 janelas de 10 (o evento so na mudanca)
                for _ in range(30):
                    ev = resumo.amostra(m.estado()["tick"], tuple(rng.random() for _ in CANAIS_TELA))
                    if ev is not None:
                        m.sentido_tela(*_niveis(ev))
            elif h % 4 == 1:
                m.trocar_canal(rng.randrange(config_tv(fonte).n_programas))
            m.avancar(HORA)
            if h % 3 == 0:
                m.deixar_comida("racao", x, y)
            if h % 5 == 2 and not m.estado()["dormindo"]:
                m.observar(AcaoUsuario.ACARICIAR)
            if h == 30:
                m.observar(AcaoUsuario.TAPA)
    finally:
        if g is not None:
            g.soltar()
    return m, cerebro, g, estimulos


def _niveis(ev):
    from digilab.events import ler_sentido_tela
    return ler_sentido_tela(ev)


def _vida(fonte: str, semente: int) -> dict:
    m, cerebro, g, estimulos = viver(fonte, semente)
    ms = cerebro.motivos
    if len(estimulos) != len(ms):
        raise RuntimeError("os estimulos e as decisoes divergem")
    decisoes = [{"k": k, "acao": ms[k]["acao"], "assinatura": g.assinaturas[k], "motivo": E.paraj(ms[k]), "estimulos": estimulos[k]}
                for k in range(len(ms))]
    olhares = sum(1 for x in ms if x["olhar"]["olha"] is not None)
    if olhares == 0:
        raise RuntimeError(f"a vida {fonte}/{semente} nunca olhou a TV")
    return {"fonte": fonte, "semente": semente, "dias": DIAS, "decisoes": decisoes, "olhares": olhares,
            "assistir": sum(1 for e in estimulos if ["atividade", "assistir"] in e),
            "agrados": sum(1 for e in estimulos if any(x[0] == "agrado_tela" for x in e)),
            "log": [ev.para_dict() for ev in m.log], "log_sha256": hashlib.sha256(m.log.para_jsonl().encode("utf-8")).hexdigest(),
            "estado": hashlib.sha256(E._texto(E.paraj(cerebro.estado_interno())).encode("utf-8")).hexdigest(),
            "assinatura_final": g.assinar(), "corpo": E.paraj(m.corpo.para_dict()), "novidades_tela": list(m.novidades_tela),
            "tv": E.paraj(m.mundo.tv.resumo())}


def _grade(semente: int) -> dict:
    tv = TV(config_tv("grade"), semente, 0, 0)
    ticks = list(range(0, 400, 7))
    em = [[t, tv.programa_em(t), [tv.em(t)[c] for c in CANAIS_TELA]] for t in ticks]
    troca = tv.trocar_canal((tv.programa_em(200) + 1) % tv.cfg.n_programas, 200)
    depois = [[t, tv.programa_em(t), [tv.em(t)[c] for c in CANAIS_TELA]] for t in range(200, 500, 11)]
    return {"semente": semente, "programas": [list(p) for p in tv.programas], "em": em, "troca": troca, "depois": depois,
            "grade": [{"inicio": s["inicio"], "fim": s["fim"], "programa": s["programa"]} for s in tv.grade]}


def _resumo() -> dict:
    rng = random.Random(derivar_semente(FLUXO_DONO, "resumo"))
    r = ResumoTela("tela")
    amostras, eventos = [], []
    for i in range(200):
        base = (i // 40) / 5
        v = tuple(min(1.0, base + rng.random() * 0.05) for _ in CANAIS_TELA)
        amostras.append(list(v))
        ev = r.amostra(i, v)
        if ev is not None:
            eventos.append([i, ev.valor])
    return {"fonte": "tela", "janela": r.janela, "amostras": amostras, "eventos": eventos}


def _grafo() -> dict:
    cc = _cc()
    gr = grafo_do_corpo(CONFIG_PADRAO, cc, taxas_de(CONFIG_PADRAO, cc), True, None, None, TELA)
    return {"quimicos": [E.paraj(q) for q in gr.quimicos], "emissores": [E.paraj(e) for e in gr.emissores],
            "orgaos": [E.paraj(o) for o in gr.orgaos], "somas": [E.paraj(s) for s in gr.somas]}


def gerar() -> dict:
    return {"versao": 1, "canais": list(CANAIS_TELA), "config_tela": asdict(TELA), "config_tv": asdict(ConfigTV(ligada=True)),
            "config_olhar": E.paraj(asdict(CONFIG_OLHAR)), "config_digibrain": E.paraj(asdict(config_vida())),
            "genomas": {str(s): genoma_visao(s).para_dict() for s in (101, 202, 303, 404, 505)},
            "genoma_vazio": genoma_visao_vazio().para_dict(), "grades": [_grade(s) for s in (101, 202)], "resumo": _resumo(),
            "grafo": _grafo(), "vidas": [_vida(f, s) for f in FONTES for s in SEMENTES]}


def texto() -> bytes:
    return E.texto_do_arquivo(gerar()).encode("utf-8")


def arquivo(bruto: bytes | None = None) -> bytes:
    """o gz (mtime 0, nivel 9) do texto"""
    return gzip.compress(texto() if bruto is None else bruto, compresslevel=9, mtime=0)


if __name__ == "__main__":
    ARQUIVO.write_bytes(arquivo())
    print("gravado", ARQUIVO, ARQUIVO.stat().st_size, "bytes")
