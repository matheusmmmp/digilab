"""Gabarito do ELOGIO, etapa 2 (docs/TAREFA_V3_ELOGIO.md, secoes 3 e 9): as vidas de hoje do DigiBrain modular que recebem o carinho do
dono pelo corpo, gravadas com o codigo de ANTES do gancho `mudanca_no_corpo` no modular, num commit proprio. Com a `ConfigElogio`
desligada, estas vidas tem de sair iguais, byte a byte.

As vidas (o modular do braco REL do laboratorio, o corpo da etapa 6 com os gestos, so as sementes dos testes):
  - `casado|<carinho>|<semente>`: o mundo com as arvores (CONFIG_MUNDO_LIGADA) e o efeito das frutas da condicao `casado` pelo genoma das
    frutas da semente (D-EL-9), 3 dias;
  - `lab|<carinho>|<semente>`: o mundo do laboratorio (o do produto, CONFIG_MUNDO_MVP), 3 dias.
O carinho vem pelo gancho `carinho` do `simular_vida_fisico`, fora do orcamento (D-EL-10): `sem` (nenhum), `cada4` (um a cada 4 passos do
dono) e `fruta` (um no passo seguinte a cada fruta comida).

De cada vida: o sha256 do log, do estado do motor e do estado interno do cerebro (com os motivos), e as contagens.

    python tests/gabarito_elogio.py     # grava tests/gabaritos/elogio_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_v2_digibrain_prototipo as orq  # noqa: E402
from bancada.mundos import efeitos_da_condicao  # noqa: E402
from bancada.regras_mundo import simular_vida_fisico  # noqa: E402
from digilab.config import CONFIG_CORPO_DRIVES, CONFIG_FRUTAS, CONFIG_MUNDO_LIGADA, CONFIG_MUNDO_MVP, CONFIG_PADRAO  # noqa: E402
from digilab.digibrain import DigiBrain  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402
from digilab.frutas import genoma_frutas  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo  # noqa: E402
from digilab.temperamento import NEUTRO  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "elogio_de_hoje.json"
SEMENTES = (101, 202)                                   # so as dos testes
DIAS = 3
DONO = "atencioso"
LUGAR = "comedouro"
CARINHOS = ("sem", "cada4", "fruta")
MUNDOS = {"casado": CONFIG_MUNDO_LIGADA, "lab": CONFIG_MUNDO_MVP}


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


class CarinhoDoGabarito:
    """o carinho das vidas do gabarito, pelo gancho `carinho` do simular_vida_fisico. O dono ve o pet comer: le (so le) os consumos do
    motor (`consumos_mundo`), que o estado() nao expoe; o motor chega pela fabrica"""

    def __init__(self, modo: str) -> None:
        self.modo = modo
        self.motor = None
        self.passos = 0
        self.vistos = 0
        self.feitos = 0

    def acoes(self, e: dict) -> list:
        self.passos += 1
        if self.modo == "cada4":
            n = 1 if self.passos % 4 == 0 else 0
        elif self.modo == "fruta":
            consumos = self.motor.consumos_mundo
            n = 1 if any(c["tipo"] != "racao" for c in consumos[self.vistos:]) else 0
            self.vistos = len(consumos)
        else:
            n = 0
        self.feitos += n
        return [AcaoUsuario.ACARICIAR] * n


def vida(mundo: str, carinho: str, semente: int):
    cm = MUNDOS[mundo]
    efeito = efeitos_da_condicao(genoma_frutas(semente, CONFIG_FRUTAS), CONFIG_FRUTAS, "casado") if mundo == "casado" else None
    cd = orq.config_do_braco("REL", None, True)
    registro = orq.Registro(DigiBrain(CONFIG_PADRAO, cd, cm, semente=semente), orq.CONFIG_DIGIBRAIN_INATOS.escala)

    c = CarinhoDoGabarito(carinho)

    def fm(p, cfg, s):
        kw = {} if efeito is None else {"efeito_frutas": efeito}
        c.motor = com_corpo(MotorMundo)(p, cfg, s, NEUTRO, "brasa", obediencia_desligada=True, cfg_mundo=cm, cfg_corpo=CONFIG_CORPO_DRIVES,
                                        **kw)
        return c.motor

    motor, _ = simular_vida_fisico(DonoComLugar(criar_dono(DONO), LUGAR, semente, DONO, cm), registro, semente, DIAS,
                                   orq.ORCAMENTO_POR_DIA * DIAS, DONO, fm, carinho=c if carinho != "sem" else None)
    return motor, orq.cerebro_de(registro), c


def impressao(mundo: str, carinho: str, semente: int) -> dict:
    motor, cerebro, c = vida(mundo, carinho, semente)
    comidas = [x["tipo"] for x in motor.consumos_mundo]
    return {"log": _sha(_texto([ev.para_dict() for ev in motor.log])), "estado": _sha(_texto(motor.estado())),
            "cerebro": _sha(_texto(cerebro.estado_interno())), "carinhos": c.feitos if carinho != "sem" else 0,
            "decisoes": cerebro.k, "frutas": sum(1 for t in comidas if t != "racao"), "racao": comidas.count("racao")}


def gerar() -> dict:
    return {f"{m}|{c}|{s}": impressao(m, c, s) for m in MUNDOS for c in CARINHOS for s in SEMENTES}


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes do gancho")
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
