"""Gabarito das vidas de hoje para a TV no jogo (GOSTO_VISUAL, as decisoes A a E da captura ligada ao cerebro; docs/registro/2026-11.md,
D-GV-TVJOGO). Gravado com o codigo da `main` antes de qualquer peca da etapa (a TV desligada, a acao IR_TV, a TV no grupo), num commit
proprio. Com as chaves novas desligadas (o padrao), estas vidas tem de sair iguais depois, byte a byte.

Tres familias, as que a etapa toca:
  - a TV de um pet so (P1c e P1d): o laboratorio com o olhar, nas duas fontes da TV, a vida do exportador do gosto visual
    (`exportar_gosto_visual.viver`), duas sementes; de cada vida, o sha256 do log, do estado interno do cerebro, do mundo fisico e do
    estado do motor, e o numero de decisoes;
  - o grupo de dois pets (o A com a entrada social, que le o `lobos.ACOES_VISIVEIS`, e o instinto): tres vidas do gabarito do grupo
    (`exportar_gabarito_grupo.vida`), o sha256 do resumo;
  - a rede de si (`rede_de_si.ACOES`, o `tuple(AcaoPet)` de hoje): o tamanho das entradas e o sha256 dos pesos iniciais.

    python tests/gabarito_tv_jogo.py     # grava tests/gabaritos/tv_jogo_vidas_de_hoje.json (so com o codigo de antes)
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

import exportar_gabarito_grupo as G  # noqa: E402
import exportar_gosto_visual as X  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "tv_jogo_vidas_de_hoje.json"
SEMENTES_TV = (101, 202)
VIDAS_GRUPO = (0, 1, 2)                           # os indices de G.VIDAS: o A e o A, o instinto e o A, o A com o corpo dos drives


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _json(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=repr)


def vida_tv(fonte: str, semente: int) -> dict:
    m, cerebro, _, _ = X.viver(fonte, semente, gravar=False)
    return {"decisoes": len(cerebro.motivos), "log": _sha(m.log.para_jsonl()), "cerebro": _sha(_json(cerebro.estado_interno())),
            "fisico": _sha(_json(m.resumo_mundo_fisico())), "estado": _sha(_json(m.estado()))}


def vida_grupo(i: int) -> dict:
    v = G.vida(*G.VIDAS[i])
    return {"resumo": v["resumo_sha256"], "eventos": len(v["registro"]["eventos"])}


def rede_de_si() -> dict:
    """as listas de hoje que leem o `tuple(AcaoPet)`: a rede de si e a entrada social do A"""
    from digilab import rede_de_si as R
    from digilab.policies import lobos as L
    return {"acoes": [a.value for a in R.ACOES], "acoes_visiveis": list(L.ACOES_VISIVEIS), "entradas_sociais": list(L.ENTRADAS_SOCIAIS)}


def gerar() -> dict:
    out = {f"tv|{f}|{s}": vida_tv(f, s) for f in X.FONTES for s in SEMENTES_TV}
    out.update({f"grupo|{G.VIDAS[i][0]}": vida_grupo(i) for i in VIDAS_GRUPO})
    out["rede_de_si"] = rede_de_si()
    return out


if __name__ == "__main__":
    ARQUIVO.write_text(json.dumps(gerar(), sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
