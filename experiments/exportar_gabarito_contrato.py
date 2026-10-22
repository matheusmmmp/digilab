"""Gabarito da paridade do contrato sensorio-motor, Python x TS (a P4, docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 4, etapa 2; a
G-PAR-CONTRATO).

Exporta, de digilab/contrato.py e do digilab/mundo.py com a ConfigContrato, o que o web/app/motor/contrato.ts e o motor/mundo.ts tem de
reproduzir com os mesmos numeros:
  config   a ConfigContrato desligada e a ligada;
  grade    as contas do contrato em casos sorteados (rng propria, semente 101): o setor, o relativo, o comprimento, o cone, a oclusao, a
           visao, o bloqueio, o movimento com o deslize, os bigodes, a grade, o A* (com e sem caminho), a celula livre mais perto, o
           controlador (com muros, contatos e bloqueio) e o empurrao da bola;
  vidas    as vidas do gabarito do mundo (experiments/exportar_gabarito_mundo.py: o instinto, o cerebro aleatorio e os lobos, os dois
           layouts, a bola perto), com as chaves ligadas: os sensores e o controlador nas quatro, mais duas com uma chave so e uma com as
           paredes. De cada uma, o traco do mundo na ordem (os gestos do dono e, por decisao, a percepcao antes, com a orientacao, os
           candidatos, o alvo, o ocorrido com o registro do contrato, o estado e a percepcao depois), o resumo e os proximos sorteios.
O TS rejoga o traco com o cerebro de teste do gabarito do mundo (o engine, a politica e o dono sao do Python): o mundo e um componente.

    python experiments/exportar_gabarito_contrato.py      # grava web/app/test/gabaritos/contrato_python.json
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

import exportar_gabarito_mundo as gm  # noqa: E402

from digilab import contrato as ct  # noqa: E402
from digilab.config import CONFIG_CONTRATO, CONFIG_CONTRATO_LIGADO, ConfigContrato  # noqa: E402
from digilab.donos import criar_dono  # noqa: E402
from digilab.mundo import DonoComLugar, simular_vida_mundo  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "contrato_python.json"
SEMENTE_GRADE = 101
PAREDES = ConfigContrato(sensores=True, controlador=True, paredes=True)
SO_SENSORES = ConfigContrato(sensores=True)
SO_CONTROLADOR = ConfigContrato(controlador=True)


def _cct(c: ConfigContrato) -> dict:
    return asdict(c)


class MotorMundoContrato(gm.MotorMundoGravado):
    """o motor que grava o traco do mundo do gabarito do mundo, com a orientacao na percepcao (so com a chave `sensores`)"""

    def _antes_da_decisao(self):
        p = super()._antes_da_decisao()
        if self.cct.sensores:
            self._op["percepcao"]["orientacao"] = p.orientacao
        return p

    def _consequencia(self, acao):
        ocorrido = super()._consequencia(acao)
        if self.cct.sensores:
            self.traco[-1]["percepcao_depois"]["orientacao"] = self._perceber(self._estado.tick).orientacao
        return ocorrido


class CerebroBorda(gm.CerebroAleatorio):
    """O cerebro aleatorio do gabarito do mundo, mas o explorar segue o alvo pendente (o `continuar`) ou vai a um ponto na borda do mapa
    (para o corpo encostar nas paredes). So para o gabarito; o TS tem o mesmo (test/contrato.test.ts)."""

    nome = "borda"

    def escolher_alvo(self, acao, cands, perc, u):
        if acao.value == "explorar":
            from digilab.mundo import Alvo
            for c in cands:
                if c.tipo == "continuar":
                    return c                                     # segue ate a borda
            k = u % 4
            if k == 0:
                return Alvo.ponto(0, (u * 13) % 480)
            if k == 1:
                return Alvo.ponto(1023, (u * 13) % 480)
            return Alvo.ponto((u * 7) % 1024, 0 if k == 2 else 479)
        return super().escolher_alvo(acao, cands, perc, u)


VIDAS = (
    {**gm.VIDAS[0], "nome": "contrato_instinto_atencioso_perto", "contrato": CONFIG_CONTRATO_LIGADO},
    {**gm.VIDAS[1], "nome": "contrato_aleatorio_aleatorio_longe", "contrato": CONFIG_CONTRATO_LIGADO},
    {**gm.VIDAS[2], "nome": "contrato_lobos_relapso_comedouro_afastado", "contrato": CONFIG_CONTRATO_LIGADO},
    {**gm.VIDAS[3], "nome": "contrato_aleatorio_atencioso_perto_bola", "contrato": CONFIG_CONTRATO_LIGADO},
    {**gm.VIDAS[1], "nome": "paredes_borda_aleatorio_longe", "semente": 505, "contrato": PAREDES,
     "politica": lambda cfg=None: CerebroBorda(cfg or gm.CONFIG_PADRAO, gm.CONFIG_BOLA)},
    {**gm.VIDAS[0], "nome": "so_sensores_instinto_atencioso_perto", "semente": 202, "contrato": SO_SENSORES},
    {**gm.VIDAS[3], "nome": "so_controlador_aleatorio_atencioso_perto_bola", "semente": 303, "contrato": SO_CONTROLADOR},
)


def vida(espec: dict) -> dict:
    cm, efeito, cc = espec["cm"], espec["efeito"], espec["contrato"]
    fm = (lambda p, cfg, s: MotorMundoContrato(p, cfg, s, obediencia_desligada=True, cfg_mundo=cm, efeito_frutas=efeito,  # noqa: E731
                                               cfg_contrato=cc))
    dono = DonoComLugar(criar_dono(espec["dono"]), espec["lugar"], espec["semente"], espec["dono"], cm)
    if espec.get("bola"):
        dono = gm.DonoComBolaPerto(dono)
    m = simular_vida_mundo(espec["dono"], dono, espec["politica"](), espec["semente"], gm.DIAS, 16 * gm.DIAS, fm,
                           rotulo_dono=espec["dono"]).motor
    resumo = m.resumo_mundo_fisico()
    del resumo["rngs"]
    proximos = {}
    for nome, r in (("arvores", m._rng_arvores), ("bola", m._rng_bola), ("sujeira", m._rng_sujeira), ("alvo", m._rng_alvo)):
        c = random.Random()
        c.setstate(r.getstate())
        proximos[nome] = {"random": [c.random() for _ in range(3)], "randrange16": [c.randrange(1 << 16) for _ in range(3)]}
    return {"nome": espec["nome"], "semente": espec["semente"], "efeito": m.efeito_frutas, "layout": cm.layout.nome,
            "mult_queda": cm.mult_queda, "contrato": _cct(cc), "cerebro": getattr(espec["politica"](), "nome", "instinto"),
            "traco": json.loads(json.dumps(m.traco)), "resumo": json.loads(json.dumps(resumo)), "proximos": proximos,
            "decisoes": len(m.decisoes_mundo)}


def _solido(s: ct.Solido) -> list:
    return [s.x0, s.y0, s.x1, s.y1, s.categoria, s.colide, s.alto]


def _solidos_sorteados(r: random.Random, n: int, largura: int, altura: int) -> tuple:
    out = []
    for _ in range(n):
        x0, y0 = r.randrange(-8, largura), r.randrange(-8, altura)
        cat = r.choice(ct.CATEGORIAS_SOLIDO)
        colide = cat != "tronco" and r.random() < 0.85
        out.append(ct.Solido(x0, y0, x0 + r.randint(1, 40), y0 + r.randint(1, 40), cat, colide, r.random() < 0.8))
    return tuple(out)


def grade() -> dict:
    r = random.Random(SEMENTE_GRADE)
    g: dict = {k: [] for k in ("setor_de", "relativo", "com_comprimento", "no_cone", "tapado", "visivel", "bloqueio_em", "mover", "bigodes",
                               "grade", "caminho", "livre_mais_perto", "controlar", "empurrar", "passo_bola")}
    for _ in range(300):
        dx, dy = r.randint(-300, 300), r.randint(-300, 300)
        g["setor_de"].append([dx, dy, ct.setor_de(dx, dy)])
        s, o = r.randrange(16), r.randrange(16)
        g["relativo"].append([s, o, ct.relativo(s, o)])
        if (dx, dy) != (0, 0):
            c = r.randint(0, 200)
            g["com_comprimento"].append([dx, dy, c, list(ct.com_comprimento(dx, dy, c))])
        cos = r.choice([1, 256, 512, 724, 1000, 1024])
        g["no_cone"].append([dx, dy, o, cos, ct.no_cone(dx, dy, o, cos)])
    for dx, dy in ((0, 0), (1, 1), (-1, 1), (5, -5), (0, 0)):           # os empates
        g["setor_de"].append([dx, dy, ct.setor_de(dx, dy)])
    for _ in range(250):
        sol = _solidos_sorteados(r, r.randint(0, 6), 200, 200)
        x0, y0, x1, y1 = r.randrange(200), r.randrange(200), r.randrange(200), r.randrange(200)
        o, raio, cos = r.randrange(16), r.choice([40, 96, 300]), r.choice([512, 724])
        g["tapado"].append([x0, y0, x1, y1, [_solido(s) for s in sol], ct.tapado(x0, y0, x1, y1, sol)])
        g["visivel"].append([x0, y0, x1, y1, o, raio, cos, [_solido(s) for s in sol], ct.visivel(x0, y0, x1, y1, o, raio, cos, sol)])
        circ = tuple((r.randrange(200), r.randrange(200), r.randint(1, 10)) for _ in range(r.randint(0, 3)))
        rr = r.randint(1, 10)
        b = ct.bloqueio_em(x0, y0, rr, sol, circ)
        g["bloqueio_em"].append([x0, y0, rr, [_solido(s) for s in sol], [list(c) for c in circ], None if b is None else list(b)])
        vx, vy = r.randint(-12, 12), r.randint(-12, 12)
        mx, my, bx, by = ct.mover(x0, y0, rr, vx, vy, sol, circ)
        g["mover"].append([x0, y0, rr, vx, vy, [_solido(s) for s in sol], [list(c) for c in circ],
                           [mx, my, None if bx is None else list(bx), None if by is None else list(by)]])
        g["bigodes"].append([x0, y0, rr, o, [_solido(s) for s in sol], 32, ct.bigodes(x0, y0, rr, o, sol, 32)])
        if not (bx is None and by is None) or r.random() < 0.3:
            pbx, pby = r.randint(-15, 15), r.randint(-15, 15)
            g["passo_bola"].append([x0, y0, 4, pbx, pby, [_solido(s) for s in sol], list(ct.passo_bola(x0, y0, 4, pbx, pby, sol))])
        if (x0, y0) != (x1, y1):
            g["empurrar"].append([x0, y0, x1, y1, list(ct.empurrar(x0, y0, x1, y1))])
    nulos = 0
    for _ in range(200):
        cx_n, cy_n = r.randint(2, 12), r.randint(2, 12)
        gg = tuple(r.random() < 0.72 for _ in range(cx_n * cy_n))
        de, para = (r.randrange(cx_n), r.randrange(cy_n)), (r.randrange(cx_n), r.randrange(cy_n))
        cam = ct.caminho(gg, cx_n, cy_n, de, para)
        nulos += cam is None
        g["caminho"].append([list(gg), cx_n, cy_n, list(de), list(para), None if cam is None else [list(c) for c in cam]])
        if any(gg):
            g["livre_mais_perto"].append([list(gg), cx_n, list(para), list(ct.livre_mais_perto(gg, cx_n, para))])
    if nulos < 10:
        raise RuntimeError(f"a grade do A* precisa de casos sem caminho: {nulos}")
    for _ in range(20):
        sol = _solidos_sorteados(r, r.randint(0, 8), 192, 160)
        rr = r.choice([4, 6])
        g["grade"].append([12, 10, 16, rr, [_solido(s) for s in sol], list(ct.grade(12, 10, 16, rr, sol))])
    casos = []
    for _ in range(150):
        casos.append(_solidos_sorteados(r, r.randint(0, 8), 192, 160))
    def muro_fino() -> ct.Solido:
        if r.random() < 0.5:
            k = r.randrange(9)
            return ct.Solido(0, 16 * k + 14, 192, 16 * k + 16, "obstaculo", True, True)
        k = r.randrange(11)
        return ct.Solido(16 * k + 14, 0, 16 * k + 16, 160, "parede", True, True)
    for _ in range(80):                                           # muros finos: os centros livres, o corpo nao passa (o contato)
        casos.append(tuple(muro_fino() for _ in range(r.randint(1, 3))))
    for _ in range(20):                                           # o pet numa caixa: sem caminho para fora
        cx, cy = 16 * r.randrange(2, 9), 16 * r.randrange(2, 7)
        casos.append((ct.Solido(cx - 16, cy - 16, cx + 32, cy - 2, "parede", True, True),
                      ct.Solido(cx - 16, cy + 18, cx + 32, cy + 32, "parede", True, True),
                      ct.Solido(cx - 16, cy - 2, cx - 2, cy + 18, "obstaculo", True, True),
                      ct.Solido(cx + 18, cy - 2, cx + 32, cy + 18, "obstaculo", True, True)))
    for sol in casos:
        x0, y0, tx, ty = r.randrange(192), r.randrange(160), r.randrange(192), r.randrange(160)
        if len(sol) == 4 and sol[0].categoria == "parede" and sol[2].categoria == "obstaculo":
            x0, y0 = sol[0].x0 + 24, sol[0].y0 + 24                 # no meio da caixa
        if ct.bloqueio_em(x0, y0, 6, sol) is not None:
            continue                                              # o pet nunca comeca dentro de um solido
        args = [x0, y0, tx, ty, r.choice([8, 16]), r.choice([1, 5, 15]), r.choice([2, 4, 7]), 6]
        o, tb = r.randrange(16), r.choice([1, 3])
        a = ct.controlar(*args, sol, 12, 10, 16, tb, o)
        g["controlar"].append({"args": args, "solidos": [_solido(s) for s in sol], "cx_n": 12, "cy_n": 10, "sub": 16, "ticks_bloqueado": tb,
                               "orientacao": o,
                               "andar": {"x": a.x, "y": a.y, "trajetoria": [list(p) for p in a.trajetoria], "andado": a.andado,
                                         "parou_por": a.parou_por, "contatos": [list(c) for c in a.contatos], "orientacao": a.orientacao}})
    return g


def gerar() -> dict:
    return {"versao": 1, "config": {"desligada": _cct(CONFIG_CONTRATO), "ligada": _cct(CONFIG_CONTRATO_LIGADO)}, "grade": grade(),
            "vidas": [vida(v) for v in VIDAS]}


if __name__ == "__main__":
    gg = gerar()
    ARQUIVO.write_text(json.dumps(gg, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): {[(v['nome'], v['decisoes'], len(v['traco'])) for v in gg['vidas']]}")
