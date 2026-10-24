"""Gabarito do laco do pet com o mundo para o MVP (docs/TAREFA_V2_MVP_MUNDO_PRODUTO.md, secao 4; a etapa 0, para o G-PAR da etapa 1).

Grava, com o codigo da `main` e ANTES de qualquer mudanca do MVP, vidas do pet com o corpo do v11 no mundo fisico de hoje: o
`com_corpo(MotorMundo)` com a ConfigCorpo das vidas do v11 (experiments/exportar_gabarito_lobos.py, o braco P1-c-tapa, o ponto do corpo
do adendo 4), o mundo `CONFIG_MUNDO_LIGADA` e o dono com lugar (o `DonoComLugar`: a racao posta num lugar do mapa). O cerebro e o da
recomendacao MV-2: o A do v11 escolhe a acao, sem as chaves do mundo, e o alvo e o padrao do motor. Uma vida a mais tem o instinto do
mundo (`PoliticaInstintoMundo`) no mesmo corpo, para o estimulo do consumo aparecer muitas vezes.

De cada vida, decisao a decisao, o traco do mundo do gabarito do mundo (experiments/exportar_gabarito_mundo.py: a percepcao, os candidatos,
o alvo, o ocorrido, o estado e a percepcao depois) e, do corpo:
  corpo_antes   os quimicos e os receptores na decisao (o corpo ja andou os ticks desde a decisao anterior);
  corpo_depois  os quimicos, os receptores e os estimulos da decisao, depois da consequencia no corpo (o andar, a comida, a bola).
E da vida inteira: o log do motor (para o replay da etapa 1), o resumo do mundo, o corpo e o estado no fim, e os proximos sorteios.
So as sementes dos testes. Nenhuma mecanica nova.

    python experiments/exportar_gabarito_mvp_mundo.py      # grava web/app/test/gabaritos/mvp_mundo_python.json
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import exportar_gabarito_mundo as gm  # noqa: E402

from digilab.config import CONFIG_MUNDO_LIGADA, CONFIG_PADRAO  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, simular_vida_mundo  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "mvp_mundo_python.json"
CM = CONFIG_MUNDO_LIGADA
DIAS = 3
# (o nome, o cerebro, o dono, o lugar da comida, a semente): so as sementes dos testes
VIDAS = (
    ("a_v11_atencioso_comedouro", "a_v11", "atencioso", "comedouro", 101),
    ("a_v11_aleatorio_perto", "a_v11", "aleatorio", "perto", 303),
    ("a_v11_incoerente_longe", "a_v11", "incoerente", "longe", 404),
    ("instinto_atencioso_comedouro", "instinto", "atencioso", "comedouro", 505),
)


def _corpo(motor) -> dict:
    c = motor.corpo
    return {"q": dict(c.q), "receptores": dict(c.receptores())}


class MotorMundoCorpoGravado(com_corpo(gm.MotorMundoGravado)):
    """o motor do mundo com o corpo, que grava o traco do mundo e o corpo em cada decisao; nao muda nada da vida"""

    def _antes_da_decisao(self):
        p = super()._antes_da_decisao()
        self._op["corpo_antes"] = _corpo(self)
        return p

    def _consequencia(self, acao):
        n = len(self.traco)
        ocorrido = super()._consequencia(acao)             # o mundo grava o op; o corpo aplica os estimulos depois
        if len(self.traco) != n + 1 or self.traco[-1]["op"] != "decisao":
            raise RuntimeError("o traco do mundo nao gravou a decisao")
        op = self.traco[-1]
        op["corpo_depois"] = {**_corpo(self), "estimulos": [list(e) for e in self._estimulos]}
        self.traco[-1] = json.loads(json.dumps(op))         # o retrato da decisao, sem referencias que o motor mude depois
        return ocorrido


def _bancada():
    return gl.bancada_v11()


def vida(nome: str, cerebro: str, dono: str, lugar: str, semente: int, cm=CM) -> dict:
    b = _bancada()
    espec = bv.EspecVida(dono, gl.BRACO_V11, semente)
    cc = b.cfg_corpo_de(espec)
    politica = b.politica(espec, CONFIG_PADRAO) if cerebro == "a_v11" else PoliticaInstintoMundo(CONFIG_PADRAO)
    fm = (lambda p, cfg, s: MotorMundoCorpoGravado(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=cc))  # noqa: E731
    d = DonoComLugar(criar_dono(dono), lugar, semente, dono, cm)
    m = simular_vida_mundo(dono, d, politica, semente, DIAS, 16 * DIAS, fm, rotulo_dono=dono).motor
    resumo = m.resumo_mundo_fisico()
    del resumo["rngs"]
    proximos = {}
    for fluxo, r in (("arvores", m._rng_arvores), ("bola", m._rng_bola), ("sujeira", m._rng_sujeira), ("alvo", m._rng_alvo)):
        c = random.Random()
        c.setstate(r.getstate())
        proximos[fluxo] = {"random": [c.random() for _ in range(3)], "randrange16": [c.randrange(1 << 16) for _ in range(3)]}
    e = m._estado
    return {"nome": nome, "cerebro": cerebro, "dono": dono, "lugar": lugar, "semente": semente, "dias": DIAS,
            "log": [ev.para_dict() for ev in m.log], "traco": m.traco, "resumo": json.loads(json.dumps(resumo)),
            "corpo_fim": _corpo(m), "estado_fim": {"fome": e.fome, "energia": e.energia, "humor": e.humor, "sujeira": e.sujeira,
                                                   "tick": e.tick},
            "proximos": proximos, "decisoes": len(m.decisoes_mundo)}


def config() -> dict:
    b = _bancada()
    cv = gl.configs_da_vida_v11(b)
    return {"corpo": json.loads(json.dumps(cv["corpo"])), "lobos": json.loads(json.dumps(cv["lobos"])),
            "consequencia": json.loads(json.dumps(cv["consequencia"])), "braco": gl.BRACO_V11, "dias": DIAS,
            "intervalo_decisao_ticks": CONFIG_PADRAO.intervalo_decisao_ticks}


def gerar() -> dict:
    return {"versao": 1, "config": config(), "vidas": [vida(*v) for v in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): "
          f"{[(v['nome'], v['decisoes'], len(v['resumo']['consumos']), len(v['log'])) for v in g['vidas']]}")
