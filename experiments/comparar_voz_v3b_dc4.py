"""A comparacao voz-v3 x voz-v3b da DC4b (CONVERSA_PET; decisao do Matheus em 2026-11-09): nas mesmas falas do dec-v3 da calibracao (as
espontaneas do E3 e os turnos de conversa com entrada dec-v3, mesmas entradas, sementes e roteiros), por braco:

- `fome_sem_conceito`: falas em que o verificador (verif-v9) achou uma afirmacao do conceito `fome` sem sustento por falta do conceito
  (`problema` = `sem_conceito`); a medida do D-CP-DC4b-5 (la contada em todas as falas; aqui so nas do dec-v3, as que a v3b refaz);
- `fome_na_fala_sem_conceito`: falas que dizem "fome" sem o conceito `fome` entre os ativos da entrada (a medida pelo texto, sem o extrator);
- `id_na_fala`: falas com um id interno solto ("P", "C1", "J1"...), a medida do D-CP-DC4b-6;
- `marcou`: falas que o verificador marcou (4.3), e `genericas`: falas que cairam na fala generica (sem verificacao).

So le os artefatos; nao chama modelo. Grava `artifacts_v3_conversa_dc4/calibracao_v3b/comparacao.json`.

    python experiments/comparar_voz_v3b_dc4.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from digilab_fala_livre import conceitos as dec  # noqa: E402

CALIBRACAO = RAIZ / "artifacts_v3_conversa_dc4" / "calibracao"
CALIBRACAO_V3B = RAIZ / "artifacts_v3_conversa_dc4" / "calibracao_v3b"
BRACOS = ("G", "H", "S")
ID_SOLTO = re.compile(r"\b(?:P|[CJ]\d+)\b")
FOME = re.compile(r"\bfome\b", re.I)


def _falas(pasta: Path) -> list[dict]:
    return [json.loads(x) for x in (pasta / "falas.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]


def _entradas(pasta: Path) -> dict:
    e = json.loads((pasta / "entradas.json").read_text(encoding="utf-8"))
    por = {x["id"]: x for x in e["E3"] + e["E2"]}
    for s in e["sequencias"]:
        por.update({x["id"]: x for x in s["entradas"]})
    return por


def fome_sem_conceito_no_verificador(r: dict) -> bool:
    v = r["verificacao"]
    return v is not None and any(a.get("conceito") == "fome" and a.get("sustentada") is False and a.get("problema") == "sem_conceito"
                                 for a in v["afirmacoes"])


def contar(regs: list[dict], entradas: dict) -> dict:
    out = {}
    for b in BRACOS:
        meus = [r for r in regs if r["braco"] == b]
        ativos = {r["id"]: {c.nome for c in dec.validar(entradas[r["entrada"]]["conceitos"]).ativos()} for r in meus}
        out[b] = {"falas": len(meus),
                  "fome_sem_conceito": sum(fome_sem_conceito_no_verificador(r) for r in meus),
                  "fome_na_fala_sem_conceito": sum(bool(FOME.search(r["fala"])) and "fome" not in ativos[r["id"]] for r in meus),
                  "id_na_fala": sum(bool(ID_SOLTO.search(r["fala"])) for r in meus),
                  "marcou": sum(r["marcou"] is True for r in meus),
                  "genericas": sum(r["marcou"] is None for r in meus)}
    return out


def comparar() -> dict:
    novas = _falas(CALIBRACAO_V3B)
    ids = {r["id"] for r in novas}
    v3 = [r for r in _falas(CALIBRACAO) if r["versao_dec"] == "dec-v3"]
    if ids != {r["id"] for r in v3} or len(ids) != len(novas):
        raise ValueError("a recalibracao nao tem exatamente as falas do dec-v3 da calibracao")
    if {r["versao_prompt"] for r in v3} != {"voz-v3"} or {r["versao_prompt"] for r in novas} != {"voz-v3b"}:
        raise ValueError("as versoes da voz nao sao a voz-v3 e a voz-v3b")
    entradas = _entradas(CALIBRACAO)
    return {"falas": "as do dec-v3 da calibracao (E3 e os turnos dec-v3 das conversas), as mesmas nas duas vozes",
            "voz-v3": contar(v3, entradas), "voz-v3b": contar(novas, entradas),
            "fonte": "artifacts_v3_conversa_dc4/calibracao/falas.jsonl (voz-v3) e calibracao_v3b/falas.jsonl (voz-v3b); entradas.json"}


def main() -> int:
    d = comparar()
    (CALIBRACAO_V3B / "comparacao.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + chr(10), encoding="utf-8", newline=chr(10))
    print(json.dumps(d, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
