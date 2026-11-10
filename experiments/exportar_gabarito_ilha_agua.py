"""Gabarito da ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA1): vidas do pet no `CONFIG_MUNDO_ILHA_AGUA` (a planta A
da ilha com o mar em volta, o rio com duas pontes e a lagoa), com o corpo, o A do v11 e as chaves dos ovos de hoje do jogo, como no
gabarito do sacudir a arvore (experiments/exportar_gabarito_arvore_sacode.py), mais o controlador do contrato (`CONFIG_CONTRATO_AGUA`),
que e quem desvia da agua.

O dono e um roteiro que testa a agua de proposito: a racao em PONTOS_COMIDA (na terra dos dois lados do rio, no rio, na lagoa e no mar),
o pet levado a PONTOS_LEVAR (idem, e fora do mapa), a bola posta em PONTOS_BOLA e as arvores sacudidas, cada um no seu passo. O gerador
confere em cada vida: nenhuma comida, nenhuma bola parada e nenhuma posicao do pet (a trajetoria tick a tick) fica na agua; o pet cruzou o
rio a pe pelo menos uma vez; e pelo menos uma comida, uma bola e um pet soltos na agua foram para a terra.

O G-PAR do laco do TS (a IA2, web/app/test/ilha_agua.test.ts) confere o TS contra este arquivo. So as sementes dos testes.

    python experiments/exportar_gabarito_ilha_agua.py      # grava web/app/test/gabaritos/ilha_agua_python.json
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import exportar_gabarito_lobos as gl  # noqa: E402
import exportar_gabarito_mvp_mundo as e0  # noqa: E402

from digilab import contrato as ct  # noqa: E402
from digilab.config import (AGUA_POR_LAYOUT, CONFIG_BOLA_NO_GOLPE_LIGADA, CONFIG_CONTRATO_AGUA, CONFIG_DECISAO_NA_COMIDA_LIGADA,  # noqa: E402
                            CONFIG_FRUTA_COMO_COMIDA_LIGADA, CONFIG_MUNDO_ILHA_AGUA, CONFIG_PADRAO, CONFIG_SACUDIR_LIGADA, TICKS_POR_DIA)
from digilab.mundo import solidos_da_agua  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "ilha_agua_python.json"
CM = CONFIG_MUNDO_ILHA_AGUA
CC = CONFIG_CONTRATO_AGUA
CS = CONFIG_SACUDIR_LIGADA
DIAS = 2
ROTEIRO_COMIDA, ROTEIRO_LEVAR, ROTEIRO_SACODE, ROTEIRO_BOLA = 97, 61, 53, 211      # fora do passo de 15 das decisoes
ROTEIRO_PONTE = 389          # a travessia: o pet solto numa cabeceira da ponte do norte e a racao posta na outra, um lado de cada vez
CABECEIRAS = ((632, 190), (744, 190))        # a oeste e a leste da ponte do norte (as celulas 42 e 43 das linhas 11 e 12)
MEIO_DA_PONTE = 704          # x do meio da ponte do norte
# em subunidades (o mapa vai de 0 a 1023 e de 0 a 479). O rio corre perto de x = 672 a 720; a lagoa, perto de (200, 370)
PONTOS_COMIDA = ((300, 240), (690, 250), (820, 200), (200, 370), (5, 5), (560, 300), (900, 330), (690, 60), (420, 120), (1020, 470))
PONTOS_LEVAR = ((640, 240), (690, 300), (850, 240), (-40, 120), (210, 372), (512, -7), (760, 100), (1500, 50), (300, 200), (0, 0))
PONTOS_BOLA = ((500, 240), (700, 150), (8, 470), (880, 260), (205, 368))
# (o nome, a semente): so as sementes dos testes; o dono "atencioso" so da o rotulo da EspecVida (a ConfigCorpo do v11)
VIDAS = (("a_v11_agua_202", 202), ("a_v11_agua_505", 505))


def motor(semente: int):
    b = e0._bancada()
    espec = bv.EspecVida("atencioso", gl.BRACO_V11, semente)
    return e0.MotorMundoCorpoGravado(b.politica(espec, CONFIG_PADRAO), CONFIG_PADRAO, semente, obediencia_desligada=True, cfg_mundo=CM,
                                     cfg_corpo=b.cfg_corpo_de(espec), cfg_decisao_comida=CONFIG_DECISAO_NA_COMIDA_LIGADA,
                                     cfg_bola_golpe=CONFIG_BOLA_NO_GOLPE_LIGADA, cfg_sacudir=CS,
                                     cfg_fruta_comida=CONFIG_FRUTA_COMO_COMIDA_LIGADA, cfg_contrato=CC)


def viver(semente: int):
    """a vida do roteiro; devolve o motor e o que o roteiro pediu (o ponto pedido e onde a coisa foi parar)"""
    m = motor(semente)
    arvores = [a[0] for a in CM.layout.arvores]
    fim, agora, k = DIAS * TICKS_POR_DIA, 0, {"c": 0, "l": 0, "s": 0, "b": 0, "p": 0}
    pedidos = {"comida": [], "levar": [], "bola": [], "ponte": [], "dormindo_em": []}
    passos = (ROTEIRO_COMIDA, ROTEIRO_LEVAR, ROTEIRO_SACODE, ROTEIRO_BOLA, ROTEIRO_PONTE)
    for t in sorted({t for t in range(1, fim + 1) if any(t % p == 0 for p in passos)} | {fim}):
        m.avancar(t - agora)
        agora = t
        if t % ROTEIRO_COMIDA == 0:
            x, y = PONTOS_COMIDA[k["c"] % len(PONTOS_COMIDA)]
            k["c"] += 1
            antes = set(m.mundo.comidas)
            m.deixar_comida("racao", x, y)
            (novo,) = set(m.mundo.comidas) - antes
            c = m.mundo.comidas[novo]
            pedidos["comida"].append({"tick": t, "pedido": [x, y], "ficou": [c["x"], c["y"]]})
        if t % ROTEIRO_LEVAR == 0:
            x, y = PONTOS_LEVAR[k["l"] % len(PONTOS_LEVAR)]
            if m._estado.dormindo:
                pedidos["dormindo_em"].append(t)
            else:
                k["l"] += 1
                m.levar_pet(x, y)
                pedidos["levar"].append({"tick": t, "pedido": [x, y], "ficou": list(m.pet)})
        if t % ROTEIRO_SACODE == 0:
            m.sacudir_arvore(arvores[k["s"] % len(arvores)])
            k["s"] += 1
        if t % ROTEIRO_BOLA == 0:
            x, y = PONTOS_BOLA[k["b"] % len(PONTOS_BOLA)]
            k["b"] += 1
            m.deixar_bola(x, y)
            bola = m.mundo.bola
            pedidos["bola"].append({"tick": t, "pedido": [x, y], "ficou": [bola["x1"], bola["y1"]]})
        if t % ROTEIRO_PONTE == 0 and not m._estado.dormindo:
            de, para = CABECEIRAS[k["p"] % 2], CABECEIRAS[(k["p"] + 1) % 2]
            k["p"] += 1
            m.levar_pet(*de)
            m.deixar_comida("racao", *para)
            pedidos["ponte"].append({"tick": t, "pet": list(de), "racao": list(para)})
    return m, pedidos


def conferir(m, pedidos: dict) -> dict:
    """os gates da agua nesta vida (G-AG-2 e G-AG-5); falha alto se algum nao vale"""
    mundo, solidos, r = m.mundo, solidos_da_agua(CM), CC.r_pet
    for c in list(mundo.comidas.values()) + [{"x": p["ficou"][0], "y": p["ficou"][1]} for p in pedidos["comida"]]:
        if not mundo.seca(c["x"], c["y"]):
            raise RuntimeError(f"comida na agua: {c}")
    for q in mundo.quedas:
        for i in q["colocadas"]:
            c = mundo.comidas.get(i)
            if c is not None and not mundo.seca(c["x"], c["y"]):
                raise RuntimeError(f"fruta na agua: {c}")
    for rol in mundo.rolagens:
        if not mundo.seca(*rol["para"]):
            raise RuntimeError(f"a bola rolou para a agua: {rol}")
    for p in pedidos["bola"]:
        if not mundo.seca(*p["ficou"]):
            raise RuntimeError(f"a bola posta na agua: {p}")
    pontos = [tuple(p["ficou"]) for p in pedidos["levar"]] + [tuple(q) for d in m.contrato_decisoes for q in (d["trajetoria"] or ())]
    for x, y in pontos:
        if ct.bloqueio_em(x, y, r, solidos) is not None:
            raise RuntimeError(f"o pet na agua: ({x}, {y})")
    # o pet cruzou o rio a pe: numa mesma decisao, a trajetoria comeca de um lado do meio da ponte e acaba do outro
    cruzou = 0
    for d in m.contrato_decisoes:
        t = d["trajetoria"]
        if t and len(t) > 1:
            cruzou += (t[0][0] < MEIO_DA_PONTE) != (t[-1][0] < MEIO_DA_PONTE)
    movidos = {k: sum(p["pedido"] != p["ficou"] for p in pedidos[k]) for k in ("comida", "levar", "bola")}
    if not cruzou or not all(movidos.values()):
        raise RuntimeError(f"o roteiro precisa de uma travessia do rio ({cruzou}) e de uma comida, um pet e uma bola tirados da agua ({movidos})")
    return {"cruzou_o_rio": cruzou, "tirados_da_agua": movidos, "posicoes_do_pet": len(pontos)}


def _vida(nome: str, semente: int) -> dict:
    m, pedidos = viver(semente)
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "pontos_fixos", semente), "dias": DIAS, "pedidos": pedidos,
            "conferido": conferir(m, pedidos), "no_galho_fim": m.no_galho()}


def gerar() -> dict:
    return {"versao": 1, "config": {**e0.config(), "dias": DIAS, "mundo": json.loads(json.dumps(asdict(CM))), "agua": list(AGUA_POR_LAYOUT[CM.layout.nome]),
                                    "contrato": asdict(CC),
                                    "sacudir": asdict(CS),
                                    "roteiro": {"comida": ROTEIRO_COMIDA, "levar": ROTEIRO_LEVAR, "sacode": ROTEIRO_SACODE, "bola": ROTEIRO_BOLA, "ponte": ROTEIRO_PONTE,
                                                "cabeceiras": CABECEIRAS,
                                                "pontos_comida": PONTOS_COMIDA, "pontos_levar": PONTOS_LEVAR, "pontos_bola": PONTOS_BOLA}},
            "vidas": [_vida(n, s) for n, s in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): {[(v['nome'], v['decisoes'], v['conferido']) for v in g['vidas']]}")
