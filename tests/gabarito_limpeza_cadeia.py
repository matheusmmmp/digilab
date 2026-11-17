"""Gabarito da LIMPEZA, LZ2b (docs/TAREFA_V3_LIMPEZA.md, 3.3): as vidas que passam pela cadeia de motores de antes do mundo, o
`MotorPersonalidade` (o vinculo, o desejo, a recusa e o motivo) e o `MotorTreino` (o treino do combate), com um cerebro que fica: o
instinto (`PoliticaInstintoBola`: o instinto com o gancho vazio do dono, que o `MotorPersonalidade`
repassa; fora do `MotorAmbiente` a bola e 0, e ele decide como o `PoliticaInstinto`). O modular so roda no mundo, e as vidas dele pela cadeia inteira (o `MotorMundo` herda o `MotorTreino`)
ja ficam no gabarito da LZ1 parte 2. Gravado com o codigo da LZ2a, ANTES da LZ2b, num commit proprio. Depois da LZ2b e da LZ4, estas vidas
tem de sair iguais, byte a byte.

As vidas:
  - `personalidade|<obediencia>|<temperamento>|<dono>|<semente>`: o `MotorPersonalidade` com a obediencia ligada e desligada, o
    temperamento neutro e um teimoso (a teimosia pesa na obediencia), pelo `simular_vida` da v1;
  - `treino|<braco>|<semente>`: o `MotorTreino` com o plano de treino do braco (o `DonoComTreino`), com o loop do `simular_vida_treino`
    e o instinto no lugar do bandit.

De cada vida: a impressao do gabarito do mundo (o log, o estado, o estado do motor, as acoes, as rngs, o estado da politica), a
personalidade (o vinculo, as recusas, os desejos) e, no treino, o estado do treino. Uma recusa de hoje fica gravada com o erro.

    python tests/gabarito_limpeza_cadeia.py     # grava tests/gabaritos/limpeza_cadeia_de_hoje.json (so com o codigo de antes da LZ2b)
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import gabarito_mundo as gm  # noqa: E402
from digilab.ambiente import PoliticaInstintoBola  # noqa: E402
from digilab.config import CONFIG_DONOS, CONFIG_PADRAO, CONFIG_TREINO, TICKS_POR_DIA  # noqa: E402
from digilab.donos import Visao, criar_dono  # noqa: E402
from digilab.personalidade import MotorPersonalidade  # noqa: E402
from digilab.protocol import derivar_semente  # noqa: E402
from digilab.temperamento import NEUTRO, Temperamento  # noqa: E402
from digilab.treino import CanalDeInteracao, simular_vida  # noqa: E402
from digilab.treino_vida import BRACOS_TREINO, DonoComTreino, MotorTreino, orcamento_treino  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "limpeza_cadeia_de_hoje.json"
SEMENTES = (101, 202)                                   # so as dos testes
DIAS = 3
ORCAMENTO = 16 * DIAS
DONOS = ("atencioso", "aleatorio")
OBEDIENCIAS = ("ligada", "desligada")
TEMPERAMENTOS = {"neutro": NEUTRO, "teimoso": Temperamento(teimosia=1.0)}
DIAS_TREINO = 6                                         # o plano de treino precisa de dias para ter sessoes
ESPECIE = "brasa"


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _texto(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=repr)


def _personalidade(m) -> dict:
    return {"personalidade": _sha(_texto(m.personalidade())), "recusas": _sha(_texto([r.para_dict() for r in m.recusas])),
            "desejos": _sha(_texto([repr(d) for d in m.desejos])), "vinculo": m.vinculo.para_dict()}


def vida_personalidade(obediencia: str, temperamento: str, dono: str, semente: int):
    t = TEMPERAMENTOS[temperamento]

    def fm(p, cfg, s):
        return MotorPersonalidade(p, cfg, s, t, obediencia_desligada=obediencia == "desligada")

    return simular_vida(dono, criar_dono(dono), PoliticaInstintoBola(CONFIG_PADRAO), semente, DIAS, ORCAMENTO, fabrica_motor=fm,
                        rotulo_dono=dono)


def vida_treino(braco: str, semente: int):
    """o loop do `simular_vida_treino`, com o instinto no lugar do bandit da personalidade"""
    cfg, cd, ct = CONFIG_PADRAO, CONFIG_DONOS, CONFIG_TREINO
    passos = DIAS_TREINO * TICKS_POR_DIA // cd.passo_ticks
    orc, _ = orcamento_treino(DIAS_TREINO, cd, ct)
    motor = MotorTreino(PoliticaInstintoBola(cfg), cfg, semente, NEUTRO, ESPECIE, cfg_treino=ct)
    dono = DonoComTreino(braco, DIAS_TREINO, cd, ct)
    rng_dono = random.Random(derivar_semente("dono", semente, braco))
    canal = CanalDeInteracao(motor, orc, cd.max_interacoes_por_passo)
    for passo in range(passos):
        motor.avancar(cd.passo_ticks)
        minimo, maximo = canal.limites(passo, passos)
        visao = Visao(estado=motor.estado(), passo=passo, passos_totais=passos, orcamento=orc, gasto=canal.gasto,
                      minimo_obrigatorio=minimo, maximo_permitido=maximo)
        canal.aplicar(dono.decidir(visao, rng_dono), passo, passos)
    canal.fechar()
    return motor, canal.gasto, dono


def impressao_personalidade(obediencia: str, temperamento: str, dono: str, semente: int) -> dict:
    try:
        v = vida_personalidade(obediencia, temperamento, dono, semente)
    except Exception as ex:                    # a recusa de hoje fica gravada, e tem de continuar igual
        return {"erro": type(ex).__name__, "mensagem": str(ex)}
    return {**gm.impressao(v.motor, v.interacoes), **_personalidade(v.motor)}


def impressao_treino(braco: str, semente: int) -> dict:
    try:
        m, gasto, dono = vida_treino(braco, semente)
    except Exception as ex:                    # a recusa de hoje fica gravada, e tem de continuar igual
        return {"erro": type(ex).__name__, "mensagem": str(ex)}
    return {**gm.impressao(m, gasto), **_personalidade(m), "treino": _sha(_texto(m.treino.__dict__)),
            "dono": dict(dono.contagem)}


def gerar() -> dict:
    out = {f"personalidade|{o}|{t}|{d}|{s}": impressao_personalidade(o, t, d, s)
           for o in OBEDIENCIAS for t in TEMPERAMENTOS for d in DONOS for s in SEMENTES}
    out.update({f"treino|{b}|{s}": impressao_treino(b, s) for b in BRACOS_TREINO for s in SEMENTES})
    return out


if __name__ == "__main__":
    if ARQUIVO.exists():
        raise SystemExit(f"{ARQUIVO} ja existe: o gabarito e gravado uma vez, com o codigo de antes da LZ2b")
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(ARQUIVO)
