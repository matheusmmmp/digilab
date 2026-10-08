"""Gabarito da paridade do mundo fisico, Python x TS (docs/TAREFA_V2_MUNDO_FISICO.md, secao 9, etapa 5; o G-PAR da secao 10).

Exporta, de digilab/mundo.py, o que o web/app/motor/mundo.ts tem de reproduzir com os mesmos numeros:
  config   a ConfigMundo (com os layouts padrao e afastado) e os numeros do estado que o mundo usa (Config);
  grade    derivar_semente, as sequencias do random.Random do Python (random, randrange, randint) em sementes pequenas e de 64 bits, a
           conta inteira (div_arred, distancia, passo_ate, deslocar, regiao_de, cheiro_em, direcao_do_cheiro) e os eventos do log
           (deixar_comida e deixar_bola, validos e invalidos);
  vidas    4 vidas inteiras de 3 dias (o instinto com o alvo padrao; um cerebro que escolhe qualquer alvo, inclusive a podre e um ponto
           lembrado; os lobos aprendendo, no layout afastado com o dobro de quedas; o mesmo cerebro com o dono que deixa a bola perto,
           para a bola rolar e a comida podre ser comida). De cada uma, o traco do mundo na ordem: os gestos
           do dono e, por decisao, a percepcao antes, o estado depois do efeito da acao, os candidatos, o alvo, o ocorrido, o estado e a
           percepcao depois; no fim, o resumo do mundo e os proximos sorteios de cada fluxo.
O TS rejoga o traco sem o resto do motor (o engine, a politica e o dono sao do Python): o mundo e um componente.

    python experiments/exportar_gabarito_mundo.py      # grava web/app/test/gabaritos/mundo_python.json
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import asdict, replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab.config import (CONFIG_LOBOS_APRENDIZ, CONFIG_MUNDO_LIGADA, CONFIG_PADRAO, LAYOUT_MUNDO_AFASTADO,  # noqa: E402
                            LAYOUT_MUNDO_PADRAO)
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import ACOES_PET_HOJE, AcaoPet, Evento, deixar_bola, deixar_comida, ler_deixar_bola, ler_deixar_comida  # noqa: E402
from digilab.mundo import (DeixarBola, DonoComLugar, MotorMundo, cheiro_em, deslocar, direcao_do_cheiro, distancia, div_arred,  # noqa: E402
                           passo_ate, regiao_de, simular_vida_mundo)
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.ambiente import PoliticaInstintoBola  # noqa: E402
from digilab.config import CONFIG_BOLA  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "mundo_python.json"
CM = CONFIG_MUNDO_LIGADA
DIAS = 3


def _estado(e) -> dict:
    return {"fome": e.fome, "energia": e.energia, "humor": e.humor, "sujeira": e.sujeira}


def _percepcao(p) -> dict:
    return {"x": p.x, "y": p.y, "regiao": p.regiao, "vistos": [list(v) for v in p.vistos], "cheiro": p.cheiro,
            "direcao_cheiro": p.direcao_cheiro, "alvo_pendente": p.alvo_pendente}


class MotorMundoGravado(MotorMundo):
    """O MotorMundo que grava o traco do mundo; nao muda nada da vida."""

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)
        self.traco: list[dict] = []
        self._op: dict | None = None
        self._cands = None

    def _antes_da_decisao(self):
        p = super()._antes_da_decisao()
        self._op = {"op": "decisao", "tick": self._estado.tick, "fome_antes": self._fome_antes, "percepcao": _percepcao(p)}
        return p

    def candidatos(self, acao, u):
        c = super().candidatos(acao, u)
        self._cands = [a.para_dict() for a in c]
        return c

    def _consequencia(self, acao):
        op, self._op, self._cands = self._op, None, None
        op.update(acao=acao.value, estado=_estado(self._estado), regra=getattr(self._pm_cerebro(), "ultima_regra", None),
                  com_gancho=getattr(self._pm_cerebro(), "escolher_alvo", None) is not None
                  and not hasattr(self._pm_cerebro(), "ve_mundo_fisico"))  # o gancho que escolhe alvo (o TS o imita); o dos lobos devolve None
        ocorrido = super()._consequencia(acao)
        op.update(candidatos=self._cands, ocorrido=ocorrido, depois=_estado(self._estado),
                  percepcao_depois=_percepcao(self._perceber(self._estado.tick)))
        self.traco.append(op)
        return ocorrido

    def _aplicar_deixar_comida(self, tipo, x, y):
        self.traco.append({"op": "deixar_comida", "tick": self._estado.tick, "tipo": tipo, "x": x, "y": y})
        super()._aplicar_deixar_comida(tipo, x, y)

    def _aplicar_deixar_bola(self, x, y):
        self.traco.append({"op": "deixar_bola", "tick": self._estado.tick, "x": x, "y": y})
        super()._aplicar_deixar_bola(x, y)


class CerebroAleatorio(PoliticaInstintoBola):
    """Escolhe a acao ao acaso e qualquer alvo: um candidato (a podre inclusive), um ponto lembrado ou o padrao."""

    nome = "aleatorio"

    def agir(self, obs, rng):
        self._ultima_regra = "aleatoria"
        return rng.choice(list(ACOES_PET_HOJE))

    def escolher_alvo(self, acao, cands, perc, u):
        k = u % (len(cands) + 2)
        if k < len(cands):
            return cands[k]
        if k == len(cands) and acao is AcaoPet.EXPLORAR:
            from digilab.mundo import Alvo
            return Alvo.ponto((u * 7) % 1024, (u * 13) % 480)
        return None


class DonoComBolaPerto:
    """O dono com lugar que, a cada 4 passos do dono, troca a ultima acao do passo por deixar a bola a 2 celulas a leste do pet (o
    mesmo numero de acoes: o orcamento fecha igual). So para o gabarito: poe a bola ao alcance para o pet brincar e ela rolar."""

    def __init__(self, base) -> None:
        self.base = base
        self.nome = base.nome

    def decidir(self, visao, rng):
        saida = list(self.base.decidir(visao, rng))
        if saida and visao.passo % 4 == 0:
            px, py = visao.estado["mundo"]["pet"]
            saida[-1] = DeixarBola(min(1023, px + 32), py)
        return saida


VIDAS = (
    {"nome": "instinto_atencioso_perto", "dono": "atencioso", "lugar": "perto", "semente": 101, "cm": CM, "efeito": None,
     "politica": lambda cfg=None: PoliticaInstintoBola(cfg or CONFIG_PADRAO, CONFIG_BOLA)},
    {"nome": "aleatorio_aleatorio_longe", "dono": "aleatorio", "lugar": "longe", "semente": 202, "cm": CM,
     "efeito": {"a": -0.1, "b": 0.0, "c": 0.1}, "politica": lambda cfg=None: CerebroAleatorio(cfg or CONFIG_PADRAO, CONFIG_BOLA)},
    {"nome": "lobos_relapso_comedouro_afastado", "dono": "relapso", "lugar": "comedouro", "semente": 303,
     "cm": replace(CM, layout=LAYOUT_MUNDO_AFASTADO, mult_queda=2.0), "efeito": None,
     "politica": lambda cfg=None: PoliticaLobos(cfg or CONFIG_PADRAO, CONFIG_LOBOS_APRENDIZ)},
    {"nome": "aleatorio_atencioso_perto_bola", "dono": "atencioso", "lugar": "perto", "semente": 404, "cm": CM, "bola": True,
     "efeito": {"a": 0.1, "b": -0.1, "c": 0.0}, "politica": lambda cfg=None: CerebroAleatorio(cfg or CONFIG_PADRAO, CONFIG_BOLA)},
)


def vida(espec: dict) -> dict:
    cm, efeito = espec["cm"], espec["efeito"]
    fm = (lambda p, cfg, s: MotorMundoGravado(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, efeito_frutas=efeito))  # noqa: E731
    dono = DonoComLugar(criar_dono(espec["dono"]), espec["lugar"], espec["semente"], espec["dono"], cm)
    if espec.get("bola"):
        dono = DonoComBolaPerto(dono)
    m = simular_vida_mundo(espec["dono"], dono, espec["politica"](), espec["semente"], DIAS, 16 * DIAS, fm,
                           rotulo_dono=espec["dono"]).motor
    resumo = m.resumo_mundo_fisico()
    del resumo["rngs"]
    proximos = {}
    for nome, r in (("arvores", m._rng_arvores), ("bola", m._rng_bola), ("sujeira", m._rng_sujeira), ("alvo", m._rng_alvo)):
        c = random.Random()
        c.setstate(r.getstate())
        proximos[nome] = {"random": [c.random() for _ in range(3)], "randrange16": [c.randrange(1 << 16) for _ in range(3)]}
    return {"nome": espec["nome"], "semente": espec["semente"], "efeito": m.efeito_frutas, "layout": cm.layout.nome,
            "mult_queda": cm.mult_queda, "traco": m.traco, "resumo": json.loads(json.dumps(resumo)), "proximos": proximos,
            "decisoes": len(m.decisoes_mundo)}


def _float(*v) -> bool:
    """o argumento era float no Python (no JSON, e no JS, 3.0 vira 3: o TS nao distingue)"""
    return any(type(x) is float for x in v)


def grade() -> dict:
    r = random.Random(20261007)
    sementes = [0, 1, 101, 202, 4294967295, 4294967296, 2**63 + 12345, derivar_semente("mundo-arvores", 101)]
    seq = {}
    for s in sementes:
        a = random.Random(s)
        seq[str(s)] = {"random": [a.random() for _ in range(8)], "randrange16": [a.randrange(16) for _ in range(8)],
                       "randint13": [a.randint(1, 3) for _ in range(8)], "randrange33": [a.randrange(33) for _ in range(8)],
                       "randint_longe": [a.randint(320, 480) for _ in range(8)], "randrange65536": [a.randrange(1 << 16) for _ in range(8)],
                       "randint310": [a.randint(3, 10) for _ in range(8)]}
    rotulos = [["mundo-arvores", 101], ["mundo-bola", 202], ["mundo-sujeira", 303], ["alvo", 101], ["dono-lugar", 101, "atencioso"],
               ["mundo-arvores", derivar_semente("mundo", 31101, 0)], ["x"], []]
    derivadas = [{"rotulos": [str(x) if isinstance(x, int) and x > 2**53 else x for x in rot], "valor": str(derivar_semente(*rot))}
                 for rot in rotulos]
    contas = {"div_arred": [], "distancia": [], "passo_ate": [], "deslocar": [], "regiao_de": [], "cheiro": [], "direcao": []}
    for _ in range(400):
        n, d = r.randint(-100000, 100000), r.randint(1, 5000)
        contas["div_arred"].append([n, d, div_arred(n, d)])
        dx, dy = r.randint(-1100, 1100), r.randint(-600, 600)
        contas["distancia"].append([dx, dy, distancia(dx, dy)])
        x, y, tx, ty, alc = r.randrange(1024), r.randrange(480), r.randint(-50, 1100), r.randint(-50, 530), r.choice([0, 1, 15, 60, 61])
        contas["passo_ate"].append([x, y, tx, ty, alc, list(passo_ate(x, y, tx, ty, alc, CM))])
        dirr, comp = r.randrange(16), r.randint(0, 600)
        contas["deslocar"].append([x, y, dirr, comp, list(deslocar(x, y, dirr, comp, CM))])
        contas["regiao_de"].append([x, regiao_de(x, CM)])
    for _ in range(150):
        fontes = [[r.randrange(1024), r.randrange(480), r.choice([32, 64])] for _ in range(r.randint(0, 6))]
        x, y = r.randrange(1024), r.randrange(480)
        if fontes and r.random() < 0.5:                      # perto de uma fonte: o gradiente existe
            x, y = min(1023, fontes[0][0] + r.randint(-60, 60)), min(479, max(0, fontes[0][1] + r.randint(-60, 60)))
            x = max(0, x)
        f = [tuple(t) for t in fontes]
        contas["cheiro"].append([x, y, fontes, cheiro_em(x, y, f, CM)])
        contas["direcao"].append([x, y, fontes, list(direcao_do_cheiro(x, y, f, CM))])
    eventos = []
    for tipo, x, y in (("racao", 0, 0), ("a", 1023, 479), ("c", 512, 240), ("x", 1, 1), ("a", 1024, 1), ("a", 1, 480), ("a", -1, 1),
                       ("b", 1.5, 2)):
        try:
            e = deixar_comida(7, tipo, x, y)
            eventos.append({"fn": "deixar_comida", "args": [7, tipo, x, y], "float": _float(x, y), "ok": True, "evento": e.para_dict()})
        except ValueError:
            eventos.append({"fn": "deixar_comida", "args": [7, tipo, x, y], "float": _float(x, y), "ok": False})
    for x, y in ((0, 0), (1023, 479), (1024, 0), (0, -1), (3.0, 4)):
        try:
            e = deixar_bola(9, x, y)
            eventos.append({"fn": "deixar_bola", "args": [9, x, y], "float": _float(x, y), "ok": True, "evento": e.para_dict()})
        except ValueError:
            eventos.append({"fn": "deixar_bola", "args": [9, x, y], "float": _float(x, y), "ok": False})
    for valor in ("racao|1|2", "a|1023|479", "a|1", "a|1|2|3", "a|1.5|2", "z|1|2", "a| 1|2", "a|-1|2", "a|1024|0", "a|01|2"):
        try:
            eventos.append({"fn": "ler_deixar_comida", "valor": valor, "ok": True, "lido": list(ler_deixar_comida(Evento(0, "deixar_comida", valor)))})
        except ValueError:
            eventos.append({"fn": "ler_deixar_comida", "valor": valor, "ok": False})
    for valor in ("1|2", "1023|479", "1|2|3", "x|2", "1024|0", "-1|0"):
        try:
            eventos.append({"fn": "ler_deixar_bola", "valor": valor, "ok": True, "lido": list(ler_deixar_bola(Evento(0, "deixar_bola", valor)))})
        except ValueError:
            eventos.append({"fn": "ler_deixar_bola", "valor": valor, "ok": False})
    return {"sequencias": seq, "derivadas": derivadas, "contas": contas, "eventos": eventos}


def config() -> dict:
    d = asdict(CM)
    d["layout"] = asdict(LAYOUT_MUNDO_PADRAO)
    return {"mundo": json.loads(json.dumps(d)), "afastado": json.loads(json.dumps(asdict(LAYOUT_MUNDO_AFASTADO))),
            "estado": {"ganho_alimentar": CONFIG_PADRAO.ganho_alimentar, "prob_sujeira_pos_refeicao": CONFIG_PADRAO.prob_sujeira_pos_refeicao,
                       "sujeira_maxima": CONFIG_PADRAO.sujeira_maxima, "intervalo_decisao_ticks": CONFIG_PADRAO.intervalo_decisao_ticks}}


def gerar() -> dict:
    return {"versao": 1, "config": config(), "grade": grade(), "vidas": [vida(v) for v in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): {[(v['nome'], v['decisoes'], len(v['traco'])) for v in g['vidas']]}")
