"""A run canonica antiga (artifacts/) continua sendo reproduzida.

Roda o orquestrador com experiments/configs/canonico.json numa pasta
temporaria (~1 min) e compara com artifacts/ em dois niveis:

  ESTRITO (so no ambiente que gerou artifacts/: mesmo sistema e mesmo Python
  major.minor, gravados em metrics.json): todo artefato byte a byte, exceto
  preflight.json (grava caminho da pasta e versao do Python) e os campos
  `ambiente`/`preflight` de metrics.json.

  PORTAVEL (qualquer ambiente): logs de vida byte a byte; todo valor discreto
  (vencedores, acoes turno a turno, contagens, veredito, nomes) identico; todo
  float com erro relativo <= TOL. Motivo: o CPython usa a libm do sistema para
  sin/cos/log/exp, e a partir do 3.12 o sum() de floats e compensado; entre
  Linux/3.11 e Windows/3.13 os floats diferem no ultimo bit (~1e-13) sem mudar
  nenhuma decisao. Qualquer decisao que vire quebra este teste.
"""

import csv
import io
import json
import platform
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "experiments"))

import run_arena  # noqa: E402

CANONICO = RAIZ / "artifacts"
TOL = 1e-9
IGNORAR_CAMPOS_METRICS = {"ambiente", "preflight", "artefatos_sha256"}


def _ambiente_canonico() -> dict:
    return json.loads((CANONICO / "metrics.json").read_text(encoding="utf-8"))["ambiente"]


def ambiente_e_o_canonico() -> bool:
    amb = _ambiente_canonico()
    mesmo_python = amb["python"].split(".")[:2] == platform.python_version().split(".")[:2]
    mesmo_sistema = amb["plataforma"].split("-")[0] == platform.system()
    return mesmo_python and mesmo_sistema


def _comparar(a, b, caminho: str, difs: list[str]) -> None:
    if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        if type(a) is not type(b):
            difs.append(f"{caminho}: tipo {type(a).__name__} x {type(b).__name__}")
        elif isinstance(a, dict):
            if set(a) != set(b):
                difs.append(f"{caminho}: chaves diferentes {sorted(set(a) ^ set(b))}")
            for k in sorted(set(a) & set(b)):
                _comparar(a[k], b[k], f"{caminho}/{k}", difs)
        elif isinstance(a, list):
            if len(a) != len(b):
                difs.append(f"{caminho}: tamanho {len(a)} x {len(b)}")
            for i, (x, y) in enumerate(zip(a, b)):
                _comparar(x, y, f"{caminho}[{i}]", difs)
        elif a != b:
            difs.append(f"{caminho}: {a!r} x {b!r}")
        return
    if isinstance(a, int) and isinstance(b, int):
        if a != b:
            difs.append(f"{caminho}: {a} x {b}")
        return
    if abs(a - b) > TOL * max(1.0, abs(a), abs(b)):
        difs.append(f"{caminho}: {a!r} x {b!r}")


def _json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _jsonl(p: Path) -> list:
    return [json.loads(linha) for linha in p.read_text(encoding="utf-8").splitlines() if linha]


def _csv(p: Path) -> list:
    linhas = list(csv.reader(io.StringIO(p.read_text(encoding="utf-8"))))
    cab, corpo = linhas[0], linhas[1:]
    flutuantes = {"pontos_a", "hp_a", "hp_b"}
    return [cab] + [[float(v) if c in flutuantes else v for c, v in zip(cab, linha)] for linha in corpo]


def comparar_com_canonico(saida: Path, estrito: bool) -> list[str]:
    """Lista de diferencas entre `saida` e artifacts/. Vazia = reproduzido."""
    difs: list[str] = []
    esperados = sorted(p.relative_to(CANONICO).as_posix() for p in CANONICO.rglob("*") if p.is_file())
    obtidos = sorted(p.relative_to(saida).as_posix() for p in saida.rglob("*") if p.is_file())
    if esperados != obtidos:
        difs.append(f"arquivos: faltam {sorted(set(esperados) - set(obtidos))}, sobram {sorted(set(obtidos) - set(esperados))}")
    for rel in esperados:
        a, b = CANONICO / rel, saida / rel
        if not b.exists() or rel == "preflight.json":
            continue
        if rel == "metrics.json":
            ma, mb = _json(a), _json(b)
            for m in (ma, mb):
                for campo in IGNORAR_CAMPOS_METRICS:
                    m.pop(campo)
            if estrito:
                if ma != mb:
                    difs.append("metrics.json: difere (estrito)")
            else:
                _comparar(ma, mb, rel, difs)
            continue
        if estrito or rel.endswith(".jsonl") and rel.startswith("vidas/"):
            if a.read_bytes() != b.read_bytes():
                difs.append(f"{rel}: bytes diferentes")
        elif rel.endswith(".jsonl"):
            _comparar(_jsonl(a), _jsonl(b), rel, difs)
        elif rel.endswith(".json"):
            _comparar(_json(a), _json(b), rel, difs)
        elif rel.endswith(".csv"):
            _comparar(_csv(a), _csv(b), rel, difs)
        else:
            difs.append(f"{rel}: tipo de artefato sem regra de comparacao")
    if estrito:
        sa, sb = _json(CANONICO / "metrics.json")["artefatos_sha256"], _json(saida / "metrics.json")["artefatos_sha256"]
        sa.pop("preflight.json")
        sb.pop("preflight.json")
        if sa != sb:
            difs.append("metrics.json[artefatos_sha256]: difere")
    return difs


def test_run_canonica_reproduz_artifacts(tmp_path):
    cfg = _json(RAIZ / "experiments" / "configs" / "canonico.json")
    cfg["saida"] = str(tmp_path / "canonico")
    caminho = tmp_path / "canonico.json"
    caminho.write_text(json.dumps(cfg), encoding="utf-8")
    assert run_arena.main(["--config", str(caminho)]) == 0
    estrito = ambiente_e_o_canonico()
    difs = comparar_com_canonico(tmp_path / "canonico", estrito)
    nivel = "ESTRITO" if estrito else "PORTAVEL"
    assert not difs, f"run canonica nao reproduz artifacts/ ({nivel}, {len(difs)} diferencas):\n" + "\n".join(difs[:30])


if __name__ == "__main__":
    # sem pytest: python tests/test_canonico_intacto.py <pasta ja rodada> [--estrito]
    difs = comparar_com_canonico(Path(sys.argv[1]), "--estrito" in sys.argv)
    print("\n".join(difs[:30]) if difs else "REPRODUZ artifacts/")
    sys.exit(1 if difs else 0)
