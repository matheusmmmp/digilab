"""Gabarito da decisao na comida (docs/TAREFA_V2_PRODUTO_FOME.md, o conserto (b)): vidas do pet v12 no mundo do produto (o
`CONFIG_MUNDO_MVP`), com o corpo e o A do v11 das vidas do gabarito do produto (experiments/exportar_gabarito_mvp_produto.py) e a
`ConfigDecisaoNaComida` ligada: a comida que o dono deixa faz o pet decidir ja no proximo passo. O dono e um roteiro, e nao o dono
sintetico com lugar: o sintetico age so no passo dele (15 ticks, o mesmo tick das decisoes), e ali a chave nao muda nada. Aqui a racao cai
no meio do intervalo (a cada ROTEIRO_COMIDA ticks, perto do pet), e o carinho a cada ROTEIRO_CARINHO. Cada vida vai com a chave ligada e
desligada (a mesma vida de hoje, para o teste mostrar a diferenca). O G-PAR do laco do TS com a chave `decidirNaComida`
(web/app/test/decisao_na_comida.test.ts) confere o TS contra este arquivo, decisao a decisao. So as sementes dos testes.

    python experiments/exportar_gabarito_decisao_na_comida.py      # grava web/app/test/gabaritos/decisao_na_comida_python.json
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

from digilab.config import CONFIG_DECISAO_NA_COMIDA, CONFIG_DECISAO_NA_COMIDA_LIGADA, CONFIG_MUNDO_MVP, CONFIG_PADRAO  # noqa: E402
from digilab.config import TICKS_POR_DIA  # noqa: E402
from digilab.events import AcaoUsuario  # noqa: E402

ARQUIVO = RAIZ / "web" / "app" / "test" / "gabaritos" / "decisao_na_comida_python.json"
CM = CONFIG_MUNDO_MVP
DIAS = 2
ROTEIRO_COMIDA = 97          # a racao: ticks que nao caem no passo de 15 das decisoes (97 = 6 x 15 + 7)
ROTEIRO_CARINHO = 53
PERTO = 48                   # a racao a 3 celulas do pet, para o lado de dentro do mapa
# (o nome, a semente): so as sementes dos testes; o dono "atencioso" so da o rotulo da EspecVida (a ConfigCorpo do v11)
VIDAS = (("a_v11_roteiro_101", 101), ("a_v11_roteiro_202", 202))


def _vida(nome: str, semente: int, ligada: bool) -> dict:
    b = e0._bancada()
    espec = bv.EspecVida("atencioso", gl.BRACO_V11, semente)
    cc = b.cfg_corpo_de(espec)
    politica = b.politica(espec, CONFIG_PADRAO)
    cdc = CONFIG_DECISAO_NA_COMIDA_LIGADA if ligada else CONFIG_DECISAO_NA_COMIDA
    m = e0.MotorMundoCorpoGravado(politica, CONFIG_PADRAO, semente, obediencia_desligada=True, cfg_mundo=CM, cfg_corpo=cc,
                                  cfg_decisao_comida=cdc)
    largura, altura = CM.celulas_x * CM.sub, CM.celulas_y * CM.sub
    fim, agora = DIAS * TICKS_POR_DIA, 0
    for t in sorted({t for t in range(1, fim + 1) if t % ROTEIRO_COMIDA == 0 or t % ROTEIRO_CARINHO == 0} | {fim}):
        m.avancar(t - agora)
        agora = t
        if t % ROTEIRO_COMIDA == 0:
            x, y = m.pet
            m.deixar_comida("racao", x + PERTO if x + PERTO < largura else x - PERTO, min(y, altura - 1))
        if t % ROTEIRO_CARINHO == 0:
            m.observar(AcaoUsuario.ACARICIAR)
    return {**e0.retrato(m, nome, "a_v11", "roteiro", "perto_do_pet", semente), "dias": DIAS, "decisao_na_comida": ligada}


def gerar() -> dict:
    return {"versao": 1, "config": {**e0.config(), "dias": DIAS, "mundo": json.loads(json.dumps(asdict(CM))),
                                    "roteiro": {"comida": ROTEIRO_COMIDA, "carinho": ROTEIRO_CARINHO, "perto": PERTO}},
            "vidas": [_vida(n, s, lig) for n, s in VIDAS for lig in (True, False)]}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO} ({ARQUIVO.stat().st_size // 1024} KiB): "
          f"{[(v['nome'], v['decisao_na_comida'], v['decisoes'], len(v['resumo']['consumos']), len(v['log'])) for v in g['vidas']]}")
