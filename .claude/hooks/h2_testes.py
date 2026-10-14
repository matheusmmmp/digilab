"""H2 (Stop): antes de encerrar o turno, com mudança em `digilab/`, `experiments/` ou `tests/`, roda um conjunto rápido de testes.

O conjunto (a suíte inteira leva ~40 min e fica no PR; o sha do engine é do H1b):
- os arquivos de teste mudados (`tests/test_*.py`);
- para cada módulo mudado `digilab/<x>.py`, `digilab/<pacote>/<x>.py` ou `experiments/<x>.py`, o `tests/test_<x>.py`, se existe;
- para cada gabarito mudado (`tests/gabaritos/<nome>`), os testes que citam o nome dele.

Se algum falha, devolve o turno ao Claude (código 2) com o resumo do pytest. **Não bloqueia duas vezes pelo mesmo motivo:** com o
`stop_hook_active` (o Claude já continuou por um bloqueio) ou com a mesma assinatura de falha da última vez (guardada fora do repositório,
na pasta temporária, por sessão), deixa encerrar.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import bloquear, git, ler_evento, raiz_do_projeto  # noqa: E402

PASTAS = ("digilab/", "experiments/", "tests/")
LIMITE_S = int(os.environ.get("DIGILAB_H2_LIMITE_S", "600"))


def mudados(raiz: Path) -> list[str]:
    """Os caminhos mudados no `git status --porcelain` (o destino, num renome), só nas pastas que importam."""
    saida = []
    for linha in git(raiz, "status", "--porcelain", "--untracked-files=all").splitlines():
        caminho = linha[3:].split(" -> ")[-1].strip().strip('"')
        if caminho.startswith(PASTAS):
            saida.append(caminho)
    return sorted(set(saida))


def conjunto_rapido(raiz: Path, caminhos: list[str]) -> list[str]:
    testes = set()
    for c in caminhos:
        p = Path(c)
        if p.parts[0] == "tests" and p.name.startswith("test_") and p.suffix == ".py":
            testes.add(c)
        elif p.suffix == ".py" and p.parts[0] in ("digilab", "experiments"):
            candidato = Path("tests") / f"test_{p.stem}.py"
            if (raiz / candidato).exists():
                testes.add(candidato.as_posix())
        elif len(p.parts) >= 2 and p.parts[:2] == ("tests", "gabaritos"):
            for t in sorted((raiz / "tests").glob("test_*.py")):
                if p.name in t.read_text(encoding="utf-8", errors="replace"):
                    testes.add(t.relative_to(raiz).as_posix())
    return sorted(t for t in testes if (raiz / t).exists())


def estado(evento: dict) -> Path:
    sessao = "".join(ch for ch in str(evento.get("session_id") or "sem-sessao") if ch.isalnum() or ch in "-_")[:80]
    return Path(tempfile.gettempdir()) / f"digilab_h2_{sessao}.json"


def main() -> None:
    evento = ler_evento()
    if evento.get("stop_hook_active"):
        return
    raiz = raiz_do_projeto(evento)
    caminhos = mudados(raiz)
    if not caminhos:
        return
    testes = conjunto_rapido(raiz, caminhos)
    if not testes:
        return
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", *testes], cwd=raiz,
                           capture_output=True, timeout=LIMITE_S)
    except subprocess.TimeoutExpired:
        return                                 # longo demais para o fim do turno: fica para a suíte do PR, sem bloquear
    if r.returncode == 0:
        estado(evento).unlink(missing_ok=True)
        return
    resumo = r.stdout.decode("utf-8", "replace").strip().splitlines()[-15:]
    assinatura = hashlib.sha256(("\n".join(testes) + "\n" + "\n".join(resumo[-3:])).encode("utf-8")).hexdigest()
    arquivo = estado(evento)
    anterior = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
    if anterior.get("assinatura") == assinatura:
        return                                 # o mesmo motivo de antes: não bloqueia de novo
    arquivo.write_text(json.dumps({"assinatura": assinatura}), encoding="utf-8")
    bloquear("H2: os testes rápidos dos arquivos mudados falharam (" + ", ".join(testes) + "):\n" + "\n".join(resumo))


if __name__ == "__main__":
    main()
