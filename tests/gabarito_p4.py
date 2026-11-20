"""P4, etapa 0 (docs/TAREFA_V2_P4_CEREBRO_MUNDO.md, secao 4): o gabarito das vidas de hoje que a P4 vai tocar, no Python, gravado com o
codigo da `main` ANTES de qualquer mudanca do contrato. Com as chaves do contrato desligadas, estas vidas tem de sair iguais depois, byte a
byte (o G2; tests/test_p4_gabaritos.py):

- **o J1** (o mundo fisico pela bancada): os bracos P0, P0z, P1 e P3 com o cerebro A, nos mundos `fisico` e `fisico_afastado`, o dono
  atencioso no comedouro e longe, nas sementes 101 e 202, na montagem simples; e o P1 e o P3 no `fisico`, na completa. A impressao e a de
  tests/gabarito_corpo_mundo.py (o log, o estado, o mundo, a politica e o registro do mundo fisico inteiro);
- **o J5 com o adendo 8** (o paladar, a fruta ao lado e os adendos 7 e 8), nos quatro bracos e nos dois protocolos, nas sementes 101 e
  202, pela fumaca da bancada do J5: o sha256 do log e o das medidas sem o custo.

    python tests/gabarito_p4.py      # grava tests/gabaritos/p4_vidas_de_hoje.json (so com o codigo de antes)
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
import gabarito_corpo_mundo as gcm  # noqa: E402
import gabarito_pqp_adendo7 as gab7  # noqa: E402

ARQUIVO = RAIZ / "tests" / "gabaritos" / "p4_vidas_de_hoje.json"
SEMENTES = (101, 202)
J1_SIMPLES = {"mundos": ("fisico", "fisico_afastado"), "bracos": ("P0", "P0z", "P1", "P3"), "lugares": ("comedouro", "longe")}
J1_COMPLETA = {"mundos": ("fisico",), "bracos": ("P1", "P3"), "lugares": ("comedouro",)}
J5_PROTOCOLOS = ("T1", "T2")


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def casos_j1():
    for nome_b, sel in (("simples", J1_SIMPLES), ("completa", J1_COMPLETA)):
        for mundo in sel["mundos"]:
            for braco in sel["bracos"]:
                for lugar in sel["lugares"]:
                    for s in SEMENTES:
                        yield (f"{nome_b}|{mundo}|{braco}|atencioso|{lugar}|{s}",
                               (nome_b, bv.EspecVida("atencioso", braco, s, None, mundo, "lobos", lugar)))


def config_j5() -> dict:
    """a fumaca da bancada do J5 com o paladar, a fruta ao lado e os adendos 7 e 8 (2 dias de fase 1 e 3 de janela)"""
    return {**gab7.config(), "adendo_8": True, "bracos": list(bv.BRACOS_PQP), "protocolos": list(J5_PROTOCOLOS),
            "sementes": list(SEMENTES)}


def vidas_j5(cfg: dict | None = None) -> dict:
    bp = bv.bancada_pqp_da_config(cfg or config_j5())
    out = {}
    for braco in bv.BRACOS_PQP:
        for protocolo in J5_PROTOCOLOS:
            for s in SEMENTES:
                v = bp.vida(bv.EspecPQP(braco, protocolo, s))
                m = bp.medir(v)
                del m["custo"]
                out[v.nome] = {"log": _sha(v.motor.log.para_jsonl()), "medidas": _sha(json.dumps(m, sort_keys=True, ensure_ascii=False))}
    return out


def vidas_j1() -> dict:
    return {chave: gcm.vida_de_hoje(*caso) for chave, caso in casos_j1()}


def gerar() -> dict:
    return {"j1": vidas_j1(), "j5_adendo8": vidas_j5()}


if __name__ == "__main__":
    g = gerar()
    ARQUIVO.write_text(json.dumps(g, sort_keys=True, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{ARQUIVO}: {len(g['j1'])} vidas do J1, {len(g['j5_adendo8'])} do J5")
