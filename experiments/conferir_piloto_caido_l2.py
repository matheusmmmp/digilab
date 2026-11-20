"""O determinismo entre o piloto da L-2 que caiu e o que rodou depois do conserto (o registro "DIGIBRAIN-MODULAR-L2-CREDITO"): so le os
logs das duas pastas (artifacts_v2_digibrain_prototipo/l2/piloto_caido_1/vidas/ e .../l2/piloto/vidas/, fora do git) e o meta.json do
piloto caido, nenhuma vida. Confere que cada vida que existe nas duas tem o mesmo sha256 de log, que o piloto caido tem as 477 vidas e o
meta.json movidos inteiros, e que as vidas so do piloto novo sao as 3 que nao tinham rodado.

    python experiments/conferir_piloto_caido_l2.py
grava artifacts_v2_digibrain_prototipo/l2/piloto_caido_1_conferencia.json
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import bancada_v2 as bv  # noqa: E402
import run_v2_digibrain_l2 as l2  # noqa: E402

L2 = RAIZ / "artifacts_v2_digibrain_prototipo" / "l2"
CAIDO, NOVO = L2 / "piloto_caido_1", L2 / "piloto"
SAIDA = L2 / "piloto_caido_1_conferencia.json"
SHA_META_CAIDO = "26f43a8b3e9d80888fff7138c3ebf35d0b35286d28bcc9a845c1e2dba415bb9c"   # o do piloto caido, antes de mover
VIDAS_CAIDO = 477


def _shas(pasta: Path) -> dict:
    return {p.relative_to(pasta).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pasta.rglob("*.jsonl"))}


def conferir() -> dict:
    if bv._sha(CAIDO / "meta.json") != SHA_META_CAIDO:
        raise RuntimeError("o meta.json do piloto caido nao e o de antes de mover")
    a, b = _shas(CAIDO / "vidas"), _shas(NOVO / "vidas")
    if len(a) != VIDAS_CAIDO:
        raise RuntimeError(f"o piloto caido tem {len(a)} logs, e nao {VIDAS_CAIDO}")
    diferentes = sorted(k for k in a if k not in b or a[k] != b[k])
    if diferentes:
        raise RuntimeError(f"vidas com o log diferente entre as duas pastas: {diferentes[:5]}")
    so_novo = sorted(set(b) - set(a))
    esperadas = len(l2.BASES["l2_piloto"]) * l2.K_PILOTO * len(l2.BRACOS) * len(l2.orq.CELULAS)
    if len(b) != esperadas or len(so_novo) != esperadas - VIDAS_CAIDO:
        raise RuntimeError(f"o piloto novo tem {len(b)} logs ({len(so_novo)} so nele)")
    return {"rotulo": "o determinismo entre o piloto da L-2 caido e o rodado depois do conserto; so leitura dos logs",
            "script": {"arquivo": l2.orq.rc._relativo(Path(__file__)), "sha256": bv._sha(Path(__file__))},
            "meta_caido_sha256": SHA_META_CAIDO, "meta_novo_sha256": bv._sha(NOVO / "meta.json"),
            "vidas_caido": len(a), "vidas_novo": len(b), "comuns_com_o_mesmo_sha": len(a), "so_no_novo": so_novo,
            "logs_caido_sha256_do_conjunto": hashlib.sha256("".join(a[k] for k in sorted(a)).encode()).hexdigest()}


if __name__ == "__main__":
    d = conferir()
    bv._gravar(SAIDA, bv._dump(d))
    print(f"gravado {l2.orq.rc._relativo(SAIDA)} (sha256 {bv._sha(SAIDA)}); {d['comuns_com_o_mesmo_sha']} iguais, so no novo: {d['so_no_novo']}")
