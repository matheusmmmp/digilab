"""Roda um gerador de gabarito (tests/gabarito_*.py) como __main__ e para na primeira politica que sai (o A, o bandit, o B, o C, a camada
unica). Imprime uma linha JSON: {"arquivo", "cerebro": nome da classe ou null, "segundos"}.
uso (da raiz do repo): python tools/cerebro_do_gabarito.py tests/gabarito_x.py
(docs/TAREFA_V3_LIMPEZA.md, 3.1; um gerador que ja tem o gabarito gravado recusa regravar e sai sem linha)"""
import json, runpy, sys, time
from pathlib import Path

RAIZ = Path.cwd()
sys.path[:0] = [str(RAIZ), str(RAIZ / "experiments"), str(RAIZ / "tests")]


class Achou(BaseException):
    pass


def armar(cls):
    orig = cls.__init__

    def novo(self, *a, **k):
        raise Achou(type(self).__name__)
    cls.__init__ = novo
    return orig


from digilab.policies import bandit, lobos, cerebro_b, cerebro_c, camada_unica  # noqa: E402
for c in (bandit.PoliticaBandit, lobos.PoliticaLobos, cerebro_b.PoliticaCerebroB, cerebro_c.PoliticaCerebroC,
          camada_unica.PoliticaCamadaUnica):
    armar(c)

arq = sys.argv[1]
t0 = time.time()
achou = None
try:
    runpy.run_path(arq, run_name="__main__")
except Achou as e:
    achou = str(e)
print(json.dumps({"arquivo": arq, "cerebro": achou, "segundos": round(time.time() - t0, 1)}), flush=True)
