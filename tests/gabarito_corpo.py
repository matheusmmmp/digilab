"""Gabarito das vidas de hoje para o CORPO (docs/TAREFA_V2_CORPO_DRIVES.md, secao 14, etapa 0; o G2 da secao 12): gravado com o codigo da
main ANTES de qualquer mudanca do corpo. Com a chave do corpo desligada, estas vidas tem de sair iguais depois, byte a byte. Cobre os
motores que o corpo vai tocar (secao 2): o `MotorComFeedback` (mundo `padrao`), o `MotorAmbiente` (`bola`) e o `MotorFrutasMundo`
(`descasado`, `mutavel`, `iguais_frutas`); P0, P1, P2 (so nos mundos das frutas) e P3; montagem simples e completa; e o so cuidado do P3
(acoplado `sem_ensino`) na completa.

    python tests/gabarito_corpo.py      # grava tests/gabaritos/corpo_vidas_de_hoje.json (so com o codigo de antes)
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))
sys.path.insert(0, str(RAIZ / "tests"))

import bancada_v2 as bv  # noqa: E402
from digilab.config import CONFIG_CONSEQUENCIA  # noqa: E402
from gabarito_mundo import LOBOS_K2, impressao  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "corpo_vidas_de_hoje.json"
# genoma None em todas: no `padrao` o genoma trocaria o motor pelo MotorPersonalidade, que o corpo recusa (secao 2)
SEMENTES = (101, 202)
MUNDOS = ("padrao", "bola", "descasado", "mutavel", "iguais_frutas")
BRACOS = ("P0", "P1", "P2", "P3")
DONOS = ("atencioso", "aleatorio")
MOTORES = ("MotorComFeedback", "MotorAmbiente", "MotorFrutasMundo")
BANCADAS = {
    "simples": bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", LOBOS_K2)),
    "completa": bv.Bancada(4, 64, cfg_lobos=bv.cfg_lobos_do_ponto("T3", LOBOS_K2), julgamento_fruta=True, montagem="completa",
                           cfg_consequencia=replace(CONFIG_CONSEQUENCIA, canais_ligados=True)),
}


def casos():
    for nome_b in BANCADAS:
        for mundo in MUNDOS:
            frutas = bv.mundo_de(mundo).frutas
            for braco in BRACOS:
                if braco == "P2" and not frutas:
                    continue                                  # a informacao so existe nos mundos das frutas
                for dono in DONOS:
                    for s in SEMENTES:
                        yield f"{nome_b}|{mundo}|{braco}|{dono}|{s}", ("vida", nome_b, bv.EspecVida(dono, braco, s, None, mundo))
                        if nome_b == "completa" and braco == "P3" and frutas:
                            yield (f"{nome_b}|{mundo}|P0<P3:sem_ensino|{dono}|{s}",
                                   ("acoplado", nome_b, bv.EspecVida(dono, braco, s, None, mundo)))


def vida_de_hoje(tipo: str, nome_b: str, espec: bv.EspecVida) -> dict:
    b = BANCADAS[nome_b]
    v = b.vida(espec)
    if tipo == "acoplado":
        v = b.acoplar(v, "P0", "sem_ensino")
    return impressao(v.motor, v.interacoes)


def gerar() -> dict:
    return {chave: vida_de_hoje(*caso) for chave, caso in casos()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(g)} vidas -> {ARQUIVO}; motores {sorted({x['motor'] for x in g.values()})}")
