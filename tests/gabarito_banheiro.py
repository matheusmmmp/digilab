"""Gabarito das vidas de hoje para o G2 do banheiro (docs/TAREFA_V2_BANHEIRO.md, secao 8; a etapa 1 da secao 9), gravado com o codigo da
main ANTES de qualquer mudanca do banheiro (origin/main f2955f7: o mundo fisico e a etapa 6 do corpo). Com a chave do banheiro desligada
(e com o `AcaoPet.ALIVIAR` no enum), estas vidas tem de sair iguais depois, byte a byte:
  - pela bancada: P0, P1 e P3 nos regimes "hoje" e "quimica" do corpo, nos mundos `padrao`, `bola` e `iguais_frutas`; P0 (lobos e
    instinto), P0z, P1 e P3 no mundo `fisico`. Os bracos do corpo com os drives novos e os gestos ainda esperam o D na bancada;
  - direto, a etapa 6 inteira (`CONFIG_CORPO_DRIVES`) com o `DonoComGestos` (com e sem tapa): o instinto, o P1 e o P3 do cerebro A com
    a chave do corpo, nos mundos padrao, bola, frutas e fisico (o MotorCorpo com o MotorMundo).
O log, o estado, o estado() do motor (a quimica do corpo inclusive), as acoes, as rngs, o registro do mundo e o estado interno da politica.

    python tests/gabarito_banheiro.py      # grava tests/gabaritos/banheiro_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
import gabarito_mundo as gm  # noqa: E402
from digilab.ambiente import DonoComBola, MotorAmbiente, PoliticaInstintoBola  # noqa: E402
from digilab.config import (CONFIG_BOLA_LIGADA, CONFIG_CONSEQUENCIA, CONFIG_CORPO_DRIVES, CONFIG_FRUTAS_LIGADA,  # noqa: E402
                            CONFIG_MUNDO_LIGADA, CONFIG_PADRAO)
from digilab.donos import criar_dono  # noqa: E402
from digilab.frutas import MotorFrutas, OfertasFrutas, PoliticaInstintoFrutas, simular_vida_frutas  # noqa: E402
from digilab.gestos import CanalMundoComGestos, DonoComGestos, simular_vida_gestos  # noqa: E402
from digilab.instinto_mundo import PoliticaInstintoMundo  # noqa: E402
from digilab.motor_corpo import com_corpo  # noqa: E402
from digilab.mundo import DonoComLugar, MotorMundo, simular_vida_mundo  # noqa: E402
from digilab.policies.lobos import PoliticaLobos  # noqa: E402
from digilab.policy import PoliticaInstinto  # noqa: E402
from digilab.treino import MotorComFeedback  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "banheiro_vidas_de_hoje.json"
DIAS = 3
ORC = 16 * DIAS
SEMENTES = (101, 202)                                   # so as dos testes
DONOS = ("atencioso", "aleatorio")
BANCADA = bv.Bancada(DIAS, ORC)
BRACOS_CORPO = ("P0-hoje", "P1-hoje", "P3-hoje", "P0-quimica", "P1-quimica", "P3-quimica")
MUNDOS_CORPO = ("padrao", "bola", "iguais_frutas")
FISICO = (("P0", "lobos"), ("P0", "instinto"), ("P0z", "lobos"), ("P1", "lobos"), ("P3", "lobos"))
DIRETOS = ("padrao", "bola", "frutas", "fisico")
CEREBROS = ("instinto", "P1", "P3")
MODOS = ("tapa", "sem_tapa")
CL_T3 = bv.cfg_lobos_do_ponto("T3")
CC = CONFIG_CORPO_DRIVES
CM = CONFIG_MUNDO_LIGADA


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def impressao(motor, interacoes: int | None = None) -> dict:
    d = gm.impressao(motor, interacoes)
    cmf = getattr(motor, "cmf", None)
    if cmf is not None and cmf.ligada:
        d["fisico"] = _sha(json.dumps(motor.resumo_mundo_fisico(), sort_keys=True, default=repr))
    return d


def casos():
    for mundo in MUNDOS_CORPO:
        for braco in BRACOS_CORPO:
            for dono in DONOS:
                for s in SEMENTES:
                    yield f"bancada|{mundo}|{braco}|{dono}|{s}", ("bancada", bv.EspecVida(dono, braco, s, None, mundo))
    for braco, cerebro in FISICO:
        for dono in DONOS:
            for s in SEMENTES:
                yield (f"bancada|fisico|{braco}~{cerebro}|{dono}|perto|{s}",
                       ("bancada", bv.EspecVida(dono, braco, s, None, "fisico", cerebro, "perto")))
    for mundo in DIRETOS:
        for cerebro in CEREBROS:
            for modo in (("tapa",) if mundo == "frutas" else MODOS):      # nas frutas o canal de hoje nao tem o SemGesto
                for dono in DONOS:
                    for s in SEMENTES:
                        yield f"direto|{mundo}|{cerebro}|{modo}|{dono}|{s}", ("direto", (mundo, cerebro, modo, dono, s))


def _politica(mundo: str, cerebro: str):
    if cerebro == "instinto":
        return {"padrao": lambda: PoliticaInstinto(CONFIG_PADRAO),
                "bola": lambda: PoliticaInstintoBola(CONFIG_PADRAO, CONFIG_BOLA_LIGADA),
                "frutas": lambda: PoliticaInstintoFrutas(CONFIG_PADRAO, None, CONFIG_FRUTAS_LIGADA),
                "fisico": lambda: PoliticaInstintoMundo(CONFIG_PADRAO)}[mundo]()
    kw = {"padrao": {}, "bola": {"cfg_bola": CONFIG_BOLA_LIGADA}, "frutas": {"cfg_frutas": CONFIG_FRUTAS_LIGADA},
          "fisico": {"cfg_mundo": CM}}[mundo]
    return bv.PoliticaDoBraco(PoliticaLobos(CONFIG_PADRAO, CL_T3, cfg_corpo=CC, **kw), bv.braco_de(cerebro), CONFIG_CONSEQUENCIA)


def _vida_direta(mundo: str, cerebro: str, modo: str, dono: str, s: int):
    p = _politica(mundo, cerebro)
    if mundo == "padrao":
        fm = lambda pp, cfg, sem: com_corpo(MotorComFeedback)(pp, cfg, sem, cfg_corpo=CC)  # noqa: E731
        return simular_vida_gestos(dono, DonoComGestos(criar_dono(dono), modo), p, s, DIAS, ORC, fabrica_motor=fm, rotulo_dono=dono)
    if mundo == "bola":
        fm = lambda pp, cfg, sem: com_corpo(MotorAmbiente)(pp, cfg, sem, obediencia_desligada=True,  # noqa: E731
                                                            cfg_bola=CONFIG_BOLA_LIGADA, cfg_corpo=CC)
        return simular_vida_gestos(dono, DonoComGestos(DonoComBola(dono, CONFIG_BOLA_LIGADA), modo), p, s, DIAS, ORC, fabrica_motor=fm,
                                   rotulo_dono=dono)
    if mundo == "frutas":
        fm = lambda pp, cfg, sem: com_corpo(MotorFrutas)(pp, cfg, sem, obediencia_desligada=True,  # noqa: E731
                                                          cfg_frutas=CONFIG_FRUTAS_LIGADA, cfg_corpo=CC)
        return simular_vida_frutas(dono, DonoComGestos(criar_dono(dono), modo), p, s, DIAS, ORC, fm, OfertasFrutas(CONFIG_FRUTAS_LIGADA),
                                   rotulo_dono=dono)
    fm = lambda pp, cfg, sem: com_corpo(MotorMundo)(pp, cfg, sem, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=CC)  # noqa: E731
    d = DonoComGestos(DonoComLugar(criar_dono(dono), "perto", s, dono, CM), modo)
    return simular_vida_mundo(dono, d, p, s, DIAS, ORC, fm, rotulo_dono=dono, canal_classe=CanalMundoComGestos)


def vida_de_hoje(tipo: str, arg) -> dict:
    if tipo == "bancada":
        v = BANCADA.vida(arg)
        return impressao(v.motor, v.interacoes)
    v = _vida_direta(*arg)
    return impressao(v.motor, v.interacoes)


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g)} vidas")
