"""Gabarito da ilha onde so a agua barra o pet (docs/TAREFA_V3_ILHA_AGUA.md, IA1): vidas do pet no `CONFIG_MUNDO_MVP_AGUA` (o mundo do
produto de hoje no jogo web, sem arvores, com o mar em volta, o rio com duas pontes e a lagoa), com o corpo, o A do v11 e as chaves dos
ovos de hoje do jogo (a decisao na comida, a bola no golpe), mais o controlador do contrato (`CONFIG_CONTRATO_AGUA`), que e quem desvia
da agua. E o mundo que o TS roda: o G-PAR do laco do TS (a IA2, web/app/test/ilha_agua.test.ts) confere o TS contra este arquivo.

O dono e um roteiro que testa a agua de proposito: a racao em PONTOS_COMIDA (na terra dos dois lados do rio, no rio, na lagoa e no mar),
o pet levado a PONTOS_LEVAR (idem, e fora do mapa) e a travessia (o pet solto numa cabeceira da ponte do norte e a racao na outra). O
gerador confere em cada vida (`conferir`, que falha alto): nenhuma comida, nenhum ponto da bola (tick a tick, em toda rolagem) e nenhuma
posicao do pet (a trajetoria tick a tick) fica na agua; o pet cruzou o rio pisando na ponte pelo menos uma vez; e pelo menos uma comida e
um pet soltos na agua foram para a terra.

O mesmo roteiro, com a bola posta pelo dono (PONTOS_BOLA) e as arvores sacudidas, roda na ilha com arvores (`CONFIG_MUNDO_ILHA_AGUA`) so
no teste do Python (tests/test_ilha_agua.py): o laco do TS de hoje nao tem o sacudir, e o deixar_bola dele nao passa pelo laco
gravado do G-PAR (o Motor do jogo o chama direto no mundo). So as sementes dos testes.

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
                            CONFIG_FRUTA_COMO_COMIDA_LIGADA, CONFIG_MUNDO_MVP_AGUA, CONFIG_PADRAO, CONFIG_SACUDIR_LIGADA, PONTE,
                            TICKS_POR_DIA)
from digilab.mundo import ID_BOLA, deslocar, distancia, div_arred, solidos_da_agua  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "ilha_agua_python.json"
CM = CONFIG_MUNDO_MVP_AGUA
CC = CONFIG_CONTRATO_AGUA
CS = CONFIG_SACUDIR_LIGADA
DIAS = 2
ROTEIRO_COMIDA, ROTEIRO_LEVAR, ROTEIRO_SACODE, ROTEIRO_BOLA = 97, 61, 53, 211      # fora do passo de 15 das decisoes
ROTEIRO_PONTE = 131          # a travessia: o pet solto numa cabeceira da ponte do norte e a racao posta na outra, um lado de cada vez
CABECEIRAS = ((664, 190), (712, 190))        # a oeste e a leste da ponte do norte
PONTE_NORTE = (42, 44, 11, 13)               # as celulas da ponte do norte: as colunas 42 e 43 das linhas 11 e 12 (x0, x1, y0, y1)
# em subunidades (o mapa vai de 0 a 1023 e de 0 a 479). O rio muda de coluna ao descer: nas linhas 13 a 20 corre de x = 640 a 687, e
# perto da nascente, de x = 672 a 735; a lagoa fica perto de (200, 370). (670, 250) e (690, 60) caem no rio
PONTOS_COMIDA = ((300, 240), (670, 250), (820, 200), (200, 370), (5, 5), (560, 300), (900, 330), (690, 60), (420, 120), (1020, 470))
PONTOS_LEVAR = ((640, 240), (690, 300), (850, 240), (-40, 120), (210, 372), (512, -7), (760, 100), (1500, 50), (300, 200), (0, 0))
PONTOS_BOLA = ((500, 240), (700, 150), (8, 470), (880, 260), (205, 368))
# (o nome, a semente): so as sementes dos testes; o dono "atencioso" so da o rotulo da EspecVida (a ConfigCorpo do v11)
VIDAS = (("a_v11_agua_202", 202), ("a_v11_agua_505", 505))


def motor(semente: int, cm=CM, com_arvores: bool = False):
    b = e0._bancada()
    espec = bv.EspecVida("atencioso", gl.BRACO_V11, semente)
    extras = {"cfg_sacudir": CS, "cfg_fruta_comida": CONFIG_FRUTA_COMO_COMIDA_LIGADA} if com_arvores else {}
    return e0.MotorMundoCorpoGravado(b.politica(espec, CONFIG_PADRAO), CONFIG_PADRAO, semente, obediencia_desligada=True, cfg_mundo=cm,
                                     cfg_corpo=b.cfg_corpo_de(espec), cfg_decisao_comida=CONFIG_DECISAO_NA_COMIDA_LIGADA,
                                     cfg_bola_golpe=CONFIG_BOLA_NO_GOLPE_LIGADA, cfg_contrato=CC, **extras)


def viver(semente: int, cm=CM, com_arvores: bool = False):
    """a vida do roteiro; devolve o motor e o que o roteiro pediu (o ponto pedido e onde a coisa foi parar). Com `com_arvores` (so no
    teste do Python, na ilha com arvores), o dono tambem poe a bola e sacode as arvores."""
    m = motor(semente, cm, com_arvores)
    arvores = [a[0] for a in cm.layout.arvores]
    if com_arvores != bool(arvores):
        raise ValueError(f"o layout {cm.layout.nome!r} e o roteiro nao combinam (com_arvores = {com_arvores})")
    fim, agora, k = DIAS * TICKS_POR_DIA, 0, {"c": 0, "l": 0, "s": 0, "b": 0, "p": 0}
    pedidos = {"comida": [], "levar": [], "bola": [], "ponte": [], "dormindo_em": []}
    passos = (ROTEIRO_COMIDA, ROTEIRO_LEVAR, ROTEIRO_PONTE) + ((ROTEIRO_SACODE, ROTEIRO_BOLA) if com_arvores else ())

    def comida(t: int, x: int, y: int) -> None:
        antes = set(m.mundo.comidas)
        m.deixar_comida("racao", x, y)
        (novo,) = set(m.mundo.comidas) - antes
        c = m.mundo.comidas[novo]
        pedidos["comida"].append({"tick": t, "id": novo, "pedido": [x, y], "ficou": [c["x"], c["y"]]})

    for t in sorted({t for t in range(1, fim + 1) if any(t % p == 0 for p in passos)} | {fim}):
        m.avancar(t - agora)
        agora = t
        if t % ROTEIRO_COMIDA == 0:
            comida(t, *PONTOS_COMIDA[k["c"] % len(PONTOS_COMIDA)])
            k["c"] += 1
        if t % ROTEIRO_LEVAR == 0:
            x, y = PONTOS_LEVAR[k["l"] % len(PONTOS_LEVAR)]
            if m._estado.dormindo:
                pedidos["dormindo_em"].append(t)
            else:
                k["l"] += 1
                m.levar_pet(x, y)
                pedidos["levar"].append({"tick": t, "pedido": [x, y], "ficou": list(m.pet)})
        if com_arvores and t % ROTEIRO_SACODE == 0:
            m.sacudir_arvore(arvores[k["s"] % len(arvores)])
            k["s"] += 1
        if com_arvores and t % ROTEIRO_BOLA == 0:
            x, y = PONTOS_BOLA[k["b"] % len(PONTOS_BOLA)]
            k["b"] += 1
            m.deixar_bola(x, y)
            bola = m.mundo.bola
            pedidos["bola"].append({"tick": t, "pedido": [x, y], "ficou": [bola["x1"], bola["y1"]]})
        if t % ROTEIRO_PONTE == 0 and not m._estado.dormindo:
            de, para = CABECEIRAS[k["p"] % 2], CABECEIRAS[(k["p"] + 1) % 2]
            k["p"] += 1
            m.levar_pet(*de)
            comida(t, *para)
            pedidos["ponte"].append({"tick": t, "pet": list(de), "racao": list(para), "ficou": list(m.pet)})
    return m, pedidos


def pontos_da_rolagem(rol: dict, atrito: int) -> list[tuple[int, int]]:
    """por onde a bola passa numa rolagem, tick a tick (a conta do `Mundo.bola_em`), da saida ao ponto final"""
    (x0, y0), (x1, y1) = rol["de"], rol["para"]
    d = distancia(x1 - x0, y1 - y0)
    meio = [(x0 + div_arred((x1 - x0) * atrito * j, d), y0 + div_arred((y1 - y0) * atrito * j, d)) for j in range(1, -(-d // atrito))]
    return [(x0, y0)] + meio + [(x1, y1)]


def travessias(m, pedidos: dict, agua) -> int:
    """quantas vezes o pet cruzou o rio pela ponte do norte: depois de solto numa cabeceira (e antes de o dono leva-lo de novo), a
    trajetoria sai do lado em que ele foi solto, pisa em celulas da ponte e chega ao outro lado sem sair dela"""
    sub = m.cmf.sub
    cx0, cx1, cy0, cy1 = PONTE_NORTE
    if any(agua[y][x] != PONTE for y in range(cy0, cy1) for x in range(cx0, cx1)):
        raise RuntimeError("a ponte do norte nao esta onde o roteiro espera")
    levadas = sorted(m._tm(p["tick"]) for p in pedidos["levar"] + pedidos["ponte"])       # no tempo do mundo, como o das decisoes
    n = 0
    for p in pedidos["ponte"]:
        ini = m._tm(p["tick"])
        fim = next((t for t in levadas if t > ini), None)
        oeste = p["pet"][0] < cx0 * sub
        pisou, cruzou = False, False
        for d in m.contrato_decisoes:
            if d["tick"] < ini or (fim is not None and d["tick"] >= fim) or not d["trajetoria"]:
                continue
            for x, y in d["trajetoria"]:
                if cx0 * sub <= x < cx1 * sub:                        # na faixa do rio: so vale se for sobre a ponte
                    pisou = cy0 * sub <= y < cy1 * sub
                elif pisou and (x >= cx1 * sub) == oeste:             # saiu da ponte pelo lado oposto ao da partida
                    cruzou = True
                    break
                else:
                    pisou = False
            if cruzou:
                break
        n += cruzou
    return n


def conferir(m, pedidos: dict) -> dict:
    """os gates da agua nesta vida (G-AG-2 e G-AG-5); falha alto se algum nao vale"""
    mundo, cm, r = m.mundo, m.cmf, CC.r_pet
    solidos, agua = solidos_da_agua(cm), AGUA_POR_LAYOUT[cm.layout.nome]
    # toda comida que ja existiu: as do dono (onde ficaram), as das arvores (as quedas e as sacudidas) e as que estao no chao
    do_dono = {p["id"]: p["ficou"] for p in pedidos["comida"]}
    # (a fruta da queda natural que o pet ja comeu nao tem a posicao guardada: confere-se a que esta no chao ou sumiu)
    das_arvores = {i: None for q in mundo.quedas for i in q["colocadas"]}
    das_arvores.update({s["caiu"]: [s["x"], s["y"]] for s in (mundo.sacudidas or ()) if s["caiu"] is not None})
    if sorted([*do_dono, *das_arvores]) != list(range(ID_BOLA + 1, mundo.prox_id)):
        raise RuntimeError("ha comida que o roteiro nao viu nascer")
    for ponto in [*do_dono.values(), *(p for p in das_arvores.values() if p is not None),
                  *([c["x"], c["y"]] for c in [*mundo.comidas.values(), *mundo.sumidas])]:
        if not mundo.seca(*ponto):
            raise RuntimeError(f"comida na agua: {ponto}")
    paradas = 0
    for rol in mundo.rolagens:
        for x, y in pontos_da_rolagem(rol, cm.atrito):
            if not mundo.seca(x, y):
                raise RuntimeError(f"a bola na agua em ({x}, {y}): {rol}")
        paradas += tuple(rol["para"]) != deslocar(*rol["de"], rol["direcao"], rol["celulas"] * cm.sub, cm)
    for p in pedidos["bola"]:
        if not mundo.seca(*p["ficou"]):
            raise RuntimeError(f"a bola posta na agua: {p}")
    pontos = [tuple(p["ficou"]) for p in pedidos["levar"] + pedidos["ponte"]] + [tuple(q) for d in m.contrato_decisoes for q in (d["trajetoria"] or ())]
    for x, y in pontos:
        if ct.bloqueio_em(x, y, r, solidos) is not None:
            raise RuntimeError(f"o pet na agua: ({x}, {y})")
    cruzou = travessias(m, pedidos, agua)
    movidos = {k: sum(p["pedido"] != p["ficou"] for p in pedidos[k]) for k in ("comida", "levar")}
    if not cruzou or not all(movidos.values()):
        raise RuntimeError(f"o roteiro precisa de uma travessia pela ponte ({cruzou}) e de uma comida e um pet tirados da agua ({movidos})")
    return {"cruzou_pela_ponte": cruzou, "tirados_da_agua": movidos, "posicoes_do_pet": len(pontos), "rolagens": len(mundo.rolagens),
            "rolagens_paradas_na_margem": int(paradas)}


def _vida(nome: str, semente: int) -> dict:
    m, pedidos = viver(semente)
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "pontos_fixos", semente), "dias": DIAS, "pedidos": pedidos,
            "conferido": conferir(m, pedidos)}


def gerar() -> dict:
    return {"versao": 1, "config": {**e0.config(), "dias": DIAS, "mundo": json.loads(json.dumps(asdict(CM))),
                                    "agua": list(AGUA_POR_LAYOUT[CM.layout.nome]), "contrato": asdict(CC),
                                    "solidos_da_agua": [[s.x0, s.y0, s.x1, s.y1] for s in solidos_da_agua(CM)],
                                    "roteiro": {"comida": ROTEIRO_COMIDA, "levar": ROTEIRO_LEVAR, "ponte": ROTEIRO_PONTE,
                                                "cabeceiras": CABECEIRAS, "pontos_comida": PONTOS_COMIDA, "pontos_levar": PONTOS_LEVAR}},
            "vidas": [_vida(n, s) for n, s in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): {[(v['nome'], v['decisoes'], v['conferido']) for v in g['vidas']]}")
