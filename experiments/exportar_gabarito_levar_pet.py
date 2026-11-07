"""Gabarito do levar pet (docs/TAREFA_V3_PEGAR_PET.md, P1; os pets v19 do jogo web): vidas do pet no mundo do produto (o
`CONFIG_MUNDO_MVP`), com o corpo e o A do v11 das vidas do gabarito do produto (experiments/exportar_gabarito_mvp_mundo.py) e a
`ConfigDecisaoNaComida` ligada, como os ovos novos do jogo. O dono e um roteiro: a racao perto do pet a cada ROTEIRO_COMIDA ticks e, a cada
ROTEIRO_LEVAR, o pet levado a um dos PONTOS, em ordem (dentro do mapa, nas bordas e fora dele: PP-4). Com o pet dormindo, o roteiro tenta
levar, o motor recusa (PP-2) e o tick vai para `dormindo_em`; o roteiro segue para o proximo ponto so quando leva.

O G-PAR do laco do TS (web/app/test/levar_pet.test.ts) confere o TS contra este arquivo, decisao a decisao e bit a bit no Node, pelo laco
gravado do G-PAR do MVP (web/app/test/laco_gravado.ts), e confere a recusa em cada tick de `dormindo_em`. So as sementes dos testes.

    python experiments/exportar_gabarito_levar_pet.py      # grava web/app/test/gabaritos/levar_pet_python.json
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

from digilab.config import CONFIG_DECISAO_NA_COMIDA_LIGADA, CONFIG_MUNDO_MVP, CONFIG_PADRAO, TICKS_POR_DIA  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "levar_pet_python.json"
CM = CONFIG_MUNDO_MVP
DIAS = 2
ROTEIRO_COMIDA = 97          # a racao: ticks fora do passo de 15 das decisoes (97 = 6 x 15 + 7), como no gabarito da decisao na comida
ROTEIRO_LEVAR = 61           # o levar: tambem fora do passo das decisoes (61 = 4 x 15 + 1), para cair no meio de um destino pendente
PERTO = 48                   # a racao a 3 celulas do pet, para o lado de dentro do mapa
# os pontos onde o dono solta o pet, em subunidades (o mapa do MVP vai de 0 a 1023 e de 0 a 479): dentro, nos cantos e fora (PP-4)
PONTOS = ((640, 240), (-40, 120), (900, 300), (1500, 50), (512, -7), (100, 600), (0, 0), (1023, 479), (-9999, 99999), (300, 200))
# (o nome, a semente): so as sementes dos testes; o dono "atencioso" so da o rotulo da EspecVida (a ConfigCorpo do v11)
VIDAS = (("a_v11_levar_101", 101), ("a_v11_levar_202", 202))


def _vida(nome: str, semente: int) -> dict:
    b = e0._bancada()
    espec = bv.EspecVida("atencioso", gl.BRACO_V11, semente)
    m = e0.MotorMundoCorpoGravado(b.politica(espec, CONFIG_PADRAO), CONFIG_PADRAO, semente, obediencia_desligada=True, cfg_mundo=CM,
                                  cfg_corpo=b.cfg_corpo_de(espec), cfg_decisao_comida=CONFIG_DECISAO_NA_COMIDA_LIGADA)
    largura, altura = CM.celulas_x * CM.sub, CM.celulas_y * CM.sub
    fim, agora, k, dormindo_em = DIAS * TICKS_POR_DIA, 0, 0, []
    for t in sorted({t for t in range(1, fim + 1) if t % ROTEIRO_COMIDA == 0 or t % ROTEIRO_LEVAR == 0} | {fim}):
        m.avancar(t - agora)
        agora = t
        if t % ROTEIRO_COMIDA == 0:
            x, y = m.pet
            m.deixar_comida("racao", x + PERTO if x + PERTO < largura else x - PERTO, min(y, altura - 1))
        if t % ROTEIRO_LEVAR == 0:
            n = len(m.log)
            try:
                m.levar_pet(*PONTOS[k % len(PONTOS)])
                k += 1
            except RuntimeError:
                if not m._estado.dormindo or len(m.log) != n:
                    raise
                dormindo_em.append(t)
    if not dormindo_em or k < len(PONTOS):
        raise RuntimeError(f"{nome}: o roteiro precisa de uma recusa com o pet dormindo e de todos os pontos ({dormindo_em}, {k})")
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "perto_do_pet", semente), "dias": DIAS, "levadas": k, "dormindo_em": dormindo_em}


def gerar() -> dict:
    return {"versao": 1, "config": {**e0.config(), "dias": DIAS, "mundo": json.loads(json.dumps(asdict(CM))),
                                    "roteiro": {"comida": ROTEIRO_COMIDA, "levar": ROTEIRO_LEVAR, "perto": PERTO,
                                                "pontos": [list(p) for p in PONTOS]}},
            "vidas": [_vida(n, s) for n, s in VIDAS]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): "
          f"{[(v['nome'], v['decisoes'], v['levadas'], v['dormindo_em'], len(v['log'])) for v in g['vidas']]}")
