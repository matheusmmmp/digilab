"""Gabarito do sacudir a arvore (docs/TAREFA_V3_ARVORE_SACODE.md, S1; os pets v20 do jogo web): vidas do pet no mundo da ilha (o
`CONFIG_MUNDO_ILHA`, o MVP com J1, J2 e J3), com o corpo e o A do v11 das vidas do gabarito do produto
(experiments/exportar_gabarito_mvp_mundo.py) e as chaves dos ovos v20: a `ConfigDecisaoNaComida`, a `ConfigBolaNoGolpe`, a `ConfigSacudir`
e a `ConfigFrutaComoComida` (AS-11) ligadas.

O dono e um roteiro: a racao perto do pet a cada ROTEIRO_COMIDA ticks e, a cada ROTEIRO_SACODE, uma rajada de sacudidas numa arvore, em
ordem (J1, J2, J3, ...), com o tamanho da rajada ciclando em RAJADAS. As rajadas de 4 esvaziam o galho (o `galho_vazio`); as frutas que o
pet nao come enchem o chao (o `chao_cheio`); o roteiro sacode tambem com o pet dormindo (vale: AS-1). O gerador confere que cada vida
tem os tres motivos, uma sacudida com o pet dormindo, uma reposicao do galho e uma fruta comida pelo pet.

O G-PAR do laco do TS (a S2, web/app/test/arvore_sacode.test.ts) confere o TS contra este arquivo, decisao a decisao e bit a bit. So as
sementes dos testes.

    python experiments/exportar_gabarito_arvore_sacode.py      # grava web/app/test/gabaritos/arvore_sacode_python.json
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import exportar_gabarito_mvp_mundo as e0  # noqa: E402

from digilab.config import (CONFIG_BOLA_NO_GOLPE_LIGADA, CONFIG_DECISAO_NA_COMIDA_LIGADA, CONFIG_FRUTA_COMO_COMIDA_LIGADA,  # noqa: E402
                            CONFIG_MUNDO_ILHA, CONFIG_PADRAO, CONFIG_SACUDIR_LIGADA, TICKS_POR_DIA)
from digilab.events import FRUTAS  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "arvore_sacode_python.json"
CM = CONFIG_MUNDO_ILHA
CS = CONFIG_SACUDIR_LIGADA
DIAS = 2
ROTEIRO_COMIDA = 97          # a racao: ticks fora do passo de 15 das decisoes (97 = 6 x 15 + 7), como no gabarito do levar pet
ROTEIRO_SACODE = 53          # as rajadas: tambem fora do passo das decisoes (53 = 3 x 15 + 8)
RAJADAS = (1, 4, 2)          # o tamanho de cada rajada, em ciclo: a de 4 esvazia o galho cheio (3)
PERTO = 48                   # a racao a 3 celulas do pet, para o lado de dentro do mapa
# (o nome, a semente): so as sementes dos testes; o dono "atencioso" so da o rotulo da EspecVida (a ConfigCorpo do v11)
VIDAS = (("a_v11_sacode_101", 101), ("a_v11_sacode_505", 505))   # as que comem fruta em 2 dias (202 e 404 nao comem)
MOTIVOS = ("caiu", "galho_vazio", "chao_cheio")


def motor(semente: int):
    b = e0._bancada()
    espec = bv.EspecVida("atencioso", gl.BRACO_V11, semente)
    return e0.MotorMundoCorpoGravado(b.politica(espec, CONFIG_PADRAO), CONFIG_PADRAO, semente, obediencia_desligada=True, cfg_mundo=CM,
                                     cfg_corpo=b.cfg_corpo_de(espec), cfg_decisao_comida=CONFIG_DECISAO_NA_COMIDA_LIGADA,
                                     cfg_bola_golpe=CONFIG_BOLA_NO_GOLPE_LIGADA, cfg_sacudir=CS,
                                     cfg_fruta_comida=CONFIG_FRUTA_COMO_COMIDA_LIGADA)


def viver(semente: int):
    m = motor(semente)
    arvores = [a[0] for a in CM.layout.arvores]
    largura, altura = CM.celulas_x * CM.sub, CM.celulas_y * CM.sub
    fim, agora, k, dormindo_em = DIAS * TICKS_POR_DIA, 0, 0, []
    for t in sorted({t for t in range(1, fim + 1) if t % ROTEIRO_COMIDA == 0 or t % ROTEIRO_SACODE == 0} | {fim}):
        m.avancar(t - agora)
        agora = t
        if t % ROTEIRO_COMIDA == 0:
            x, y = m.pet
            m.deixar_comida("racao", x + PERTO if x + PERTO < largura else x - PERTO, min(y, altura - 1))
        if t % ROTEIRO_SACODE == 0:
            if m._estado.dormindo:
                dormindo_em.append(t)
            for _ in range(RAJADAS[k % len(RAJADAS)]):
                m.sacudir_arvore(arvores[k % len(arvores)])
            k += 1
    return m, dormindo_em


def _proximos(m) -> dict:
    c = random.Random()
    c.setstate(m.mundo.rng_sacode.getstate())
    return {"random": [c.random() for _ in range(3)], "randrange16": [c.randrange(1 << 16) for _ in range(3)]}


def _vida(nome: str, semente: int) -> dict:
    m, dormindo_em = viver(semente)
    sac = m.mundo.sacudidas
    motivos = {s["motivo"] for s in sac}
    frutas_comidas = [c for c in m.consumos_mundo if c["tipo"] in FRUTAS]
    depois, reposicoes = {}, 0              # o galho que cada arvore deixou na sacudida anterior; uma reposicao e um galho maior agora
    for s in sac:
        reposicoes += s["arvore"] in depois and s["no_galho_antes"] > depois[s["arvore"]]
        depois[s["arvore"]] = s["no_galho_antes"] - (s["motivo"] == "caiu")
    if not set(MOTIVOS) <= motivos or not dormindo_em or not frutas_comidas or not reposicoes:
        raise RuntimeError(f"{nome}: o roteiro precisa dos motivos {MOTIVOS} ({sorted(motivos)}), de uma sacudida dormindo "
                           f"({dormindo_em[:3]}), de uma reposicao ({reposicoes}) e de uma fruta comida ({len(frutas_comidas)})")
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "perto_do_pet", semente), "dias": DIAS, "dormindo_em": dormindo_em,
            "sacudidas": len(sac), "caidas": sum(s["motivo"] == "caiu" for s in sac), "frutas_comidas": len(frutas_comidas),
            "no_galho_fim": m.no_galho(), "proximos_sacode": _proximos(m)}


def gerar() -> dict:
    return {"versao": 1, "config": {**e0.config(), "dias": DIAS, "mundo": json.loads(json.dumps(asdict(CM))), "sacudir": asdict(CS),
                                    "roteiro": {"comida": ROTEIRO_COMIDA, "sacode": ROTEIRO_SACODE, "rajadas": list(RAJADAS),
                                                "perto": PERTO}},
            "vidas": [_vida(n, s) for n, s in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): "
          f"{[(v['nome'], v['decisoes'], v['sacudidas'], v['caidas'], v['frutas_comidas'], v['dormindo_em'][:2]) for v in g['vidas']]}")
