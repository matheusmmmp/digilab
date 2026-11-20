"""O gabarito da voz-v4 antes da voz-v4b (CONVERSA_PET, DC5a2; D-DC5B-5; CLAUDE.md: o gabarito e gravado num commit proprio, antes da
mudanca).

Grava, para as entradas fixas do gabarito da voz do jogo (`exportar_gabarito_voz_jogo_dc5`), as mensagens que a voz-v4 monta
(`prompt.mensagens_voz(..., voz=VERSAO_VOZ_V4)`), na fala espontanea (com e sem as falas ja ditas) e na conversa (com historico, [J] e
comando), com e sem um bloco de estilo. O teste `tests/test_conversa_dc5a2.py` confere que o codigo de hoje da o mesmo, byte a byte: a
voz-v4b e uma versao nova, e a voz-v4 da calibracao da DC5b nao muda.

    python experiments/exportar_gabarito_voz_v4_dc5.py --saida experiments/configs/v3_conversa_dc5/gabarito_voz_v4.json

So biblioteca padrao. Nenhuma chamada a modelo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import exportar_gabarito_voz_jogo_dc5 as gvj  # noqa: E402

from digilab_fala_livre import conceitos as dec  # noqa: E402
from digilab_fala_livre import prompt as pr  # noqa: E402

DITAS = ["Tô aqui, pensando numa coisa.", "Hmm, quero comer."]
ESTILO = "ESTILO DA ESPÉCIE (só tom; não é fato, não sustenta nada e não se cita)\nVocê é um Agumon."


def mensagens_v4() -> dict:
    out = {}
    for e, est, sit in gvj.CASOS:
        c = dec.validar(gvj.ENTRADAS[e])
        for estilo in (None, ESTILO):
            chave = f"{e}/{est}/{sit}/{'estilo' if estilo else 'sem_estilo'}"
            if sit == "conversa":
                out[chave] = pr.mensagens_voz(c, est, sit, "você lutou ontem, né?", gvj.HISTORICO, estilo=estilo, comando=True,
                                              voz=pr.VERSAO_VOZ_V4)
            else:
                out[chave] = pr.mensagens_voz(c, est, sit, estilo=estilo, voz=pr.VERSAO_VOZ_V4)
                out[chave + "/ditas"] = pr.mensagens_voz(c, est, sit, estilo=estilo, voz=pr.VERSAO_VOZ_V4, ditas=DITAS)
    return out


def gabarito() -> dict:
    d = {"voz_v4": mensagens_v4()}
    texto = json.dumps(d, ensure_ascii=False, sort_keys=True)
    return {"sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(), **d}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="o gabarito da voz-v4 antes da voz-v4b")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args(argv)
    Path(a.saida).write_text(json.dumps(gabarito(), ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
